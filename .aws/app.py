import aws_cdk as cdk

from aws_stack import CloudRecommendationStack


app = cdk.App()
CloudRecommendationStack(app, "CloudRecommendationStack")

app.synth()
