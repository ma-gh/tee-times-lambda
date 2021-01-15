#!/usr/bin/env python3
import os

from aws_cdk import (
    aws_events,
    aws_events_targets,
    aws_lambda,
    aws_s3,
    aws_sns,
    aws_sns_subscriptions,
    core,
)

GET_COURSES_LAMBDA_NAME = "GetCoursesLambda"
GET_TEE_TIMES_LAMBDA_NAME = "GetTeeTimesLambda"
NOTIFY_LAMBDA_NAME = "NotifyTeeTimesLambda"


class TeeTimesStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Webapp API Lambdas
        self.lambda_layers = self.create_lambda_layers()
        self.get_courses_lambda = self.create_lambda(
            GET_COURSES_LAMBDA_NAME, "api_lambdas.get_courses", self.lambda_layers
        )
        self.get_tee_times_lambda = self.create_lambda(
            GET_TEE_TIMES_LAMBDA_NAME, "api_lambdas.get_tee_times", self.lambda_layers
        )

        # Notify Lambda
        self.notify_topic = self.create_notify_topic()
        self.notify_bucket = self.create_notify_bucket()
        self.notify_lambda = self.create_notify_lambda(self.notify_topic, self.notify_bucket)

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
            code=aws_lambda.Code.asset("./src"),
            timeout=core.Duration.seconds(300),
            layers=layers,
        )

    def create_notify_lambda(self, notify_topic, notify_bucket):
        _lambda = self.create_lambda(
            NOTIFY_LAMBDA_NAME, "notify_lambda.notify_tee_times", self.lambda_layers
        )

        _lambda.add_environment("EARLIEST_TIME", os.environ["EARLIEST_TIME"])
        _lambda.add_environment("LATEST_TIME", os.environ["LATEST_TIME"])
        _lambda.add_environment("COURSES", os.environ["COURSES"])
        _lambda.add_environment("OUTPUT_TOPIC_ARN", notify_topic.topic_arn)
        _lambda.add_environment("NOTIFY_TEE_TIMES_BUCKET_NAME", notify_bucket.bucket_name)

        rule = aws_events.Rule(
            self,
            f"{NOTIFY_LAMBDA_NAME}Rule",
            schedule=aws_events.Schedule.cron(
                minute="*/1", hour="*", month="*", week_day="*", year="*"
            ),
        )
        rule.add_target(aws_events_targets.LambdaFunction(_lambda))

        notify_topic.grant_publish(_lambda)
        notify_bucket.grant_read_write(_lambda)

        return _lambda

    def create_notify_topic(self, topic_name="NotifyTeeTimesTopic"):
        topic = aws_sns.Topic(self, id=topic_name, display_name=topic_name)
        for email in os.environ["OUTPUT_TOPIC_EMAILS"].split(","):
            topic.add_subscription(aws_sns_subscriptions.EmailSubscription(email))
        for number in os.environ["OUTPUT_TOPIC_NUMBERS"].split(","):
            topic.add_subscription(aws_sns_subscriptions.SmsSubscription(number))
        return topic

    def create_notify_bucket(self):
        bucket = aws_s3.Bucket(
            self,
            "NotifyTeeTimesBucket",
            lifecycle_rules=[aws_s3.LifecycleRule(expiration=core.Duration.days(1))],
        )
        return bucket


app = core.App()
TeeTimesStack(app, "TeeTimes")
app.synth()
