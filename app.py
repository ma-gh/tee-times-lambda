#!/usr/bin/env python3

from aws_cdk import aws_lambda, core


class TeeTimesStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.lambda_layers = self.create_lambda_layers()
        self.get_courses_lambda = self.create_lambda(
            "GetCoursesLambda", "handler.get_courses", self.lambda_layers
        )
        self.get_tee_times_lambda = self.create_lambda(
            "GetTeeTimesLambda", "handler.get_tee_times", self.lambda_layers
        )

    def create_lambda_layers(self):
        return [
            aws_lambda.LayerVersion.from_layer_version_arn(
                self,
                "RequestsLayer",
                "arn:aws:lambda:us-west-1:770693421928:layer:Klayers-python38-requests:13",
            ),
        ]

    def create_lambda(self, lambda_name, lambda_handler_path, layers):
        return aws_lambda.Function(
            self,
            lambda_name,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler=lambda_handler_path,
            code=aws_lambda.Code.asset("./lambda"),
            timeout=core.Duration.seconds(300),
            layers=layers,
        )


app = core.App()
TeeTimesStack(app, "TeeTimes")
app.synth()
