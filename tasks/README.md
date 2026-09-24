# Tasks

The task package defines the six public manipulation tasks and their seed
skills:

- `door_push`
- `push_to_goal`
- `peg_insert`
- `peg_channel`
- `grasp_place`
- `obstacle_reach`

Each task has a typed objective, scene configuration, and allowed skill
structure. Seed YAML files are inputs to initialization modes; they are not
runtime logs. See the catalog and protocol documentation for the exact record
used in a paper replay.
