import * as path from "path";
import * as cdk from "aws-cdk-lib";
import { Platform } from "aws-cdk-lib/aws-ecr-assets";
import * as iam from "aws-cdk-lib/aws-iam";
import * as agentcore from "aws-cdk-lib/aws-bedrockagentcore";
import { Construct } from "constructs";

export class BoundedAutonomyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const modelId = this.node.tryGetContext("modelId") as string;
    const resolvedModelId = modelId.startsWith("eu.") ? modelId : `eu.${modelId}`;

    const artifact = agentcore.AgentRuntimeArtifact.fromAsset(
      path.join(process.cwd(), "agent"),
      {
        platform: Platform.LINUX_ARM64,
        extraHash: `${this.account}-${this.region}`,
      },
    );

    const runtime = new agentcore.Runtime(this, "Runtime", {
      runtimeName: "boundedAutonomy",
      description:
        "Compare raw-batch, sequential for-loop, and parallel Strands subagents",
      agentRuntimeArtifact: artifact,
      environmentVariables: {
        MODEL_ID: resolvedModelId,
        AWS_REGION: this.region,
        AWS_DEFAULT_REGION: this.region,
        LOG_LEVEL: "INFO",
      },
      lifecycleConfiguration: {
        idleRuntimeSessionTimeout: cdk.Duration.minutes(5),
        maxLifetime: cdk.Duration.minutes(30),
      },
    });

    runtime.addToRolePolicy(
      new iam.PolicyStatement({
        sid: "BedrockInvoke",
        actions: [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:GetInferenceProfile",
        ],
        resources: [
          "arn:aws:bedrock:*::foundation-model/*",
          `arn:aws:bedrock:${this.region}:${this.account}:inference-profile/*`,
          `arn:aws:bedrock:${this.region}:${this.account}:application-inference-profile/*`,
        ],
      }),
    );

    // Newer Anthropic models on Bedrock require Marketplace entitlements.
    runtime.addToRolePolicy(
      new iam.PolicyStatement({
        sid: "BedrockMarketplace",
        actions: [
          "aws-marketplace:ViewSubscriptions",
          "aws-marketplace:Subscribe",
        ],
        resources: ["*"],
      }),
    );

    new cdk.CfnOutput(this, "AgentRuntimeArn", {
      description: "Invoke this runtime with scripts/bench.py or the AWS CLI",
      value: runtime.agentRuntimeArn,
    });

    new cdk.CfnOutput(this, "AgentRuntimeId", {
      value: runtime.agentRuntimeId,
    });

    new cdk.CfnOutput(this, "ModelId", {
      value: resolvedModelId,
    });
  }
}
