## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4191 | 0.29 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4170 | 0.28 | ❌ rejected |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4173 | 0.29 | ✅ accepted |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ❌ rejected |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.419) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.06
  weight: 0.2
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
  weight: 0.3
- id: reach_goal
  metric: goal_progress
  offset:
  - 0.0
  - 0.04
  - 0.0
  weight: 0.5
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.419
- **task_score** (E): 0.294
- **fitness_score**: 0.538  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.2101 |
| contact_1 | 0.33 | 0.0648 |
| push_1 | 1.00 | 0.1415 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.124, 0.108) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 |
| contact_1 | contact | 0.33 / step_budget | (0.513, 0.124, 0.108)→(0.503, 0.120, 0.045) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 |
| push_1 | push | 1.00 / step_budget | (0.503, 0.120, 0.045)→(0.498, -0.021, 0.037) | (0.503, 0.080, 0.034)→(0.506, -0.033, 0.032) | 0.160→0.049 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- terminal_score: 0.484
- phase_score: 0.844
- phase_breakdown.reach_goal_score: 0.841
- phase_breakdown.reach_approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.484
- **Median Q (composite search score)**: 0.455
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.447


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18286,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.21389,"contact_1.contact_force_threshold":2.46662,"contact_1.contact_speed":0.03072,"push_1.push_speed":0.03888},"optimized_scores":{"best_composite_score":0.47005,"best_fitness_score":0.70005,"best_task_score":0.48403},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":315.0,"contact_point_centroid":[0.49885,0.05204,0.04754],"force_p95":39.43615,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.10369,"mean_force":12.36929,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49164,0.06258,0.03283]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":324.0,"contact_point_centroid":[0.52541,0.02036,0.03944],"force_p95":35.04517,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.7748,"mean_force":9.73594,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49214,0.0466,0.03304]},{"body_a":"peg","body_b":"channel_base_body","contact_count":221.0,"contact_point_centroid":[0.50407,0.03922,0.0096],"force_p95":24.18261,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.74808,"mean_force":7.00644,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49133,0.0798,0.03291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":483.0,"contact_point_centroid":[0.49626,0.11902,0.00939],"force_p95":0.60196,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55881,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49111,0.1794,0.19981]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49949,0.19904,0.29675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":521.0,"contact_point_centroid":[0.49603,0.11925,0.00948],"force_p95":0.59087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65193,"mean_force":0.53781,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48641,0.15901,0.0699]}],"total_contact_groups":6},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50567,-0.0492,0.0351],"final_tcp_position":[0.49555,-0.02119,0.03493],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"phases":[{"n_steps":508.0,"n_steps_budget":630.0,"object_pos_end":[0.49603,0.11908,0.03388],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19922,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.48409,0.16087,0.10951],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08724,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11918,0.03392],"object_pos_start":[0.49603,0.11908,0.03388],"object_to_goal_dist_end":0.19931,"object_to_goal_dist_start":0.19922,"object_z_max":0.03428,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.49126,0.15803,0.03495],"tcp_start":[0.48409,0.16087,0.10951],"tcp_to_object_dist_end":0.03916,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.50567,-0.0492,0.0351],"object_pos_start":[0.49602,0.11918,0.03392],"object_to_goal_dist_end":0.0317,"object_to_goal_dist_start":0.19931,"object_z_max":0.03775,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.49555,-0.02119,0.03493],"tcp_start":[0.49126,0.15803,0.03495],"tcp_to_object_dist_end":0.02978,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15217,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16233,"contact_1.contact_force_threshold":5.87688,"contact_1.contact_speed":0.02651,"push_1.push_speed":0.05779},"optimized_scores":{"best_composite_score":0.33257,"best_fitness_score":0.56257,"best_task_score":0.30652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":181.0,"contact_point_centroid":[0.52532,-0.00099,0.03841],"force_p95":29.79521,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.46365,"mean_force":7.8879,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49852,0.02786,0.03476]},{"body_a":"attachment","body_b":"peg","contact_count":212.0,"contact_point_centroid":[0.50331,0.01878,0.04855],"force_p95":29.5226,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.42426,"mean_force":8.44574,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49864,0.03022,0.03476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.50568,0.01431,0.00961],"force_p95":18.15871,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.37476,"mean_force":4.4735,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50013,0.05451,0.0354]},{"body_a":"peg","body_b":"channel_base_body","contact_count":596.0,"contact_point_centroid":[0.50571,0.063,0.00936],"force_p95":0.56333,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56927,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51191,0.15209,0.1982]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50003,0.19798,0.2958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":347.0,"contact_point_centroid":[0.50607,0.06288,0.00938],"force_p95":0.55236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54656,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51377,0.10526,0.07244]}],"total_contact_groups":6},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50813,-0.04891,0.03677],"final_tcp_position":[0.49637,-0.02121,0.0348],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"phases":[{"n_steps":624.0,"n_steps_budget":870.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.52454,0.10801,0.1067],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08764,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.063,0.03381],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.50459,0.1029,0.03849],"tcp_start":[0.52454,0.10801,0.1067],"tcp_to_object_dist_end":0.0402,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.50813,-0.04891,0.03677],"object_pos_start":[0.50593,0.063,0.03381],"object_to_goal_dist_end":0.0323,"object_to_goal_dist_start":0.14326,"object_z_max":0.03842,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.49637,-0.02121,0.0348],"tcp_start":[0.50459,0.1029,0.03849],"tcp_to_object_dist_end":0.03015,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18831,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15521,"contact_1.contact_force_threshold":6.79964,"contact_1.contact_speed":0.02416,"push_1.push_speed":0.03692},"optimized_scores":{"best_composite_score":0.45473,"best_fitness_score":0.3514,"best_task_score":0.09031},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":298.0,"contact_point_centroid":[0.50454,0.02017,0.00862],"force_p95":72.71376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.58476,"mean_force":12.92926,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50502,0.03781,0.04838]},{"body_a":"attachment","body_b":"peg","contact_count":90.0,"contact_point_centroid":[0.50686,0.00607,0.04234],"force_p95":77.85243,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.09967,"mean_force":41.04263,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50159,-7e-05,0.04264]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52557,0.0979,0.05996],"force_p95":75.32691,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.32691,"mean_force":75.32691,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51371,0.09832,0.06169]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52521,0.09803,0.05995],"force_p95":47.00393,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.45799,"mean_force":19.19151,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51337,0.09813,0.0611]},{"body_a":"peg","body_b":"channel_base_body","contact_count":619.0,"contact_point_centroid":[0.50587,0.05663,0.00936],"force_p95":0.60058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51525,0.14892,0.19792]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50015,0.19777,0.29551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":223.0,"contact_point_centroid":[0.5062,0.05666,0.00938],"force_p95":0.55019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55053,"mean_force":0.54673,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5219,0.09996,0.08405]}],"total_contact_groups":7},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50421,0.00012,0.02452],"final_tcp_position":[0.50112,-0.02016,0.04086],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"phases":[{"n_steps":648.0,"n_steps_budget":930.0,"object_pos_end":[0.50615,0.05662,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.53096,0.10195,0.10633],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08907,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05661,0.03378],"object_pos_start":[0.50615,0.05662,0.03378],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.51365,0.09832,0.06152],"tcp_start":[0.53096,0.10195,0.10633],"tcp_to_object_dist_end":0.05065,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.50421,0.00012,0.02452],"object_pos_start":[0.50615,0.05661,0.03378],"object_to_goal_dist_end":0.08171,"object_to_goal_dist_start":0.13689,"object_z_max":0.0408,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50112,-0.02016,0.04086],"tcp_start":[0.51365,0.09832,0.06152],"tcp_to_object_dist_end":0.02623,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```