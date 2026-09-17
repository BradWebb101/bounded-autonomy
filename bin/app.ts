#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { BoundedAutonomyStack } from "../lib/bounded-autonomy-stack";

const app = new cdk.App();

new BoundedAutonomyStack(app, "BoundedAutonomy", {
  description:
    "Single AgentCore runtime: raw batch vs sequential agents vs parallel Strands subagents",
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION ?? "eu-west-1",
  },
});
