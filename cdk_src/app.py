#!/usr/bin/env python3

from aws_cdk import core

from scratch_pad.scratch_pad_stack import ScratchPadStack


app = core.App()
ScratchPadStack(app, "scratch-pad")

app.synth()
