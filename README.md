# todoist-pipline

> Track completed items from todoist

![pipeline](images/todoist_pipeline.jpg "aws pipeline")

## Goal 

- Set up a pipeline to persist completed items from Todoist within the AWS environment

- Data to be loaded on a weekly basis via AWS Lambda + AWS Eventbridge Scheduler

- Persist data within S3

### To Do:

- [x] ~~Write Python script to get completed items from the previous week~~

- [X] ~~Convert timezone to AEST in csv output~~

- [x] ~~Create function to convert local datetime parameters to utc~~ 

- [x] ~~Method of scheduling script: AWS Lambda + AWS Eventbridge Scheduler~~

- [x] ~~Method of persisting date: S3~~
