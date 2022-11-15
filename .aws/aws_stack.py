from aws_cdk import Stack
from constructs import Construct

import core
import components


class CloudRecommendationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create core infrastructure
        users_table, users_params_table, shows_table, shows_params_table, recommendations_table = core.create_tables(
            self
        )
        api_gateway_role, api_gateway = core.create_api(
            self
        )
        sync_data_queue, generate_recommendations_queue = core.create_sqs(
            self,
            api_gateway_role
        )

        # Create data sync
        components.create_data_sync(
            self,
            api_gateway_role,
            api_gateway,
            sync_data_queue,
            users_table,
            users_params_table,
            shows_table,
            shows_params_table
        )

        # Create model
        inference_model_function = components.create_inference_model(
            self
        )
        train_model_function = components.create_training_model(self)

        # Generate recommendations
        components.create_generate_recommendations(
            self,
            api_gateway_role,
            api_gateway,
            generate_recommendations_queue,
            recommendations_table,
            users_params_table,
            shows_table,
            shows_params_table,
            inference_model_function
        )

        # Get recommendations
        components.create_get_recommendations(
            self,
            api_gateway,
            recommendations_table
        )

        # Train recommendation model
        components.create_train_recommendation_model(
            self,
            users_table,
            users_params_table,
            shows_params_table,
            train_model_function
        )
