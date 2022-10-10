# todoist-pipline

> Track completed items from todoist

## Goal 

- Set up a pipeline to persist completed items from Todoist within the AWS environment

- Data to be loaded on a weekly basis via AWS Lambda 

- TBD: Persist data either within S3, Aurora 

### To Do:

- [x] Write Python script to get completed items from the previous week

- [X] Convert timezone to AEST

- [ ] Create function to convert local datetime parameters to utc 

- [ ] Set up function to run on AWS Lambda 

