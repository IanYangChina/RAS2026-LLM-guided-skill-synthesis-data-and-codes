## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3662 | 0.43 | ❌ rejected |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.4029 | 0.50 | ✅ accepted |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.366) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.3
- id: push_complete
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.025
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: pre_contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.09
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_complete
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.366
- **task_score** (E): 0.426
- **fitness_score**: 0.576  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2067 |
| descend_1 | 1.00 | 1.00 | 0.0781 |
| push_1 | 1.00 | 1.00 | 0.1429 |
| retract_1 | 1.00 | 1.00 | 0.1387 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.133, 0.108) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.576 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.133, 0.108)→(0.500, 0.107, 0.037) | (0.503, 0.080, 0.034)→(0.502, 0.077, 0.035) | 0.160→0.157 | 1.00 / 1.667 | 2.252 | 104.979 |
| push_1 | push | 1.00 / step_budget | (0.500, 0.107, 0.037)→(0.497, -0.036, 0.033) | (0.502, 0.077, 0.035)→(0.505, -0.058, 0.037) | 0.157→0.031 | 1.00 / 3.333 | 52.392 | 68.215 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.036, 0.033)→(0.494, -0.036, 0.171) | (0.505, -0.058, 0.037)→(0.503, -0.059, 0.031) | 0.031→0.026 | 1.00 / 1.000 | 0.579 | 157.435 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.905
- alignment_error: None
- force_efficiency: 0.462
- terminal_score: 0.359
- phase_score: 0.778
- phase_breakdown.pre_contact_score: 0.599
- phase_breakdown.push_complete_score: 0.855

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.611
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.703
- **Median Q (composite search score)**: 0.362
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55346,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08764,"push_1.push_distance":0.16476,"push_1.push_speed":0.05654},"optimized_scores":{"best_composite_score":0.36177,"best_fitness_score":0.57177,"best_task_score":0.70317},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":138.0,"contact_point_centroid":[0.47495,-0.00104,0.04521],"force_p95":384.24678,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":418.97911,"mean_force":231.94977,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48676,-0.00101,0.04335]},{"body_a":"attachment","body_b":"peg","contact_count":625.0,"contact_point_centroid":[0.49604,0.05133,0.03337],"force_p95":132.35877,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.21468,"mean_force":73.57167,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48717,0.05686,0.03174]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":568.0,"contact_point_centroid":[0.52658,0.03517,0.03213],"force_p95":112.64518,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.48543,"mean_force":66.93661,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48695,0.04935,0.03163]},{"body_a":"attachment","body_b":"peg","contact_count":99.0,"contact_point_centroid":[0.49777,-0.00356,0.04037],"force_p95":119.59656,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.8003,"mean_force":59.20091,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48676,-0.00108,0.03849]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":165.0,"contact_point_centroid":[0.52746,-0.00355,0.03224],"force_p95":108.47239,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.48075,"mean_force":35.81942,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48678,-0.00103,0.04338]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":258.0,"contact_point_centroid":[0.475,0.03747,0.03362],"force_p95":98.61205,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.78963,"mean_force":76.49006,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,0.03748,0.03175]},{"body_a":"peg","body_b":"channel_base_body","contact_count":587.0,"contact_point_centroid":[0.5096,0.02849,0.00952],"force_p95":86.06526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.21938,"mean_force":49.79667,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48708,0.0528,0.03173]},{"body_a":"peg","body_b":"channel_base_body","contact_count":774.0,"contact_point_centroid":[0.49959,-0.02674,0.00843],"force_p95":22.51308,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.28271,"mean_force":3.35825,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48423,-0.0004,0.10551]},{"body_a":"peg","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.51688,0.03582,0.06802],"force_p95":63.85337,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.139,"mean_force":34.31944,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4869,0.04719,0.03163]},{"body_a":"peg","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.51705,-0.0108,0.06929],"force_p95":47.77001,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.13957,"mean_force":34.31092,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48677,-0.00089,0.03299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.49637,0.11615,0.00949],"force_p95":6.02212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.89351,"mean_force":1.02,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48644,0.15715,0.07014]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.49398,0.13496,0.05076],"force_p95":8.96125,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.7458,"mean_force":6.37649,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49068,0.14686,0.03966]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,-0.05524,0.02416],"force_p95":6.62219,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.71145,"mean_force":2.22364,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4836,-0.00029,0.11036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":562.0,"contact_point_centroid":[0.49626,0.11917,0.00943],"force_p95":0.61305,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55371,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49111,0.1843,0.20085]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49953,0.1993,0.29767]}],"total_contact_groups":15},"final_pose_error":0.01145,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49706,-0.03217,0.02415],"final_tcp_position":[0.48398,-0.00029,0.17073],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":418.97911,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11921,0.03399],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19934,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.63801,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":586.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.4841,0.17012,0.10945],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.49667,0.1159,0.03531],"object_pos_start":[0.49601,0.11921,0.03399],"object_to_goal_dist_end":0.19598,"object_to_goal_dist_start":0.19934,"object_z_max":0.03546,"peak_contact_force":6.01015,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":492.0,"raw_peak_contact_force":10.89351,"subtask_id":"pre_contact","tcp_end":[0.49135,0.14543,0.03518],"tcp_start":[0.4841,0.17012,0.10945],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.51291,-0.0075,0.03885],"object_pos_start":[0.49667,0.1159,0.03531],"object_to_goal_dist_end":0.07365,"object_to_goal_dist_start":0.19598,"object_z_max":0.03954,"peak_contact_force":144.14062,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2588.0,"raw_peak_contact_force":148.21468,"subtask_id":"push_complete","tcp_end":[0.48683,-0.0003,0.03182],"tcp_start":[0.49135,0.14543,0.03518],"tcp_to_object_dist_end":0.02795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":844.0,"n_steps_budget":930.0,"object_pos_end":[0.49706,-0.03217,0.02415],"object_pos_start":[0.51291,-0.0075,0.03885],"object_to_goal_dist_end":0.05047,"object_to_goal_dist_start":0.07365,"object_z_max":0.04098,"peak_contact_force":0.6436,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1212.0,"raw_peak_contact_force":418.97911,"tcp_end":[0.48398,-0.00029,0.17073],"tcp_start":[0.48683,-0.0003,0.03182],"tcp_to_object_dist_end":0.15058,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41573,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06576,"push_1.push_distance":0.16167,"push_1.push_speed":0.05609},"optimized_scores":{"best_composite_score":0.40057,"best_fitness_score":0.61057,"best_task_score":0.3594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":259.0,"contact_point_centroid":[0.5252,-0.00423,0.03652],"force_p95":22.23467,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.91178,"mean_force":5.88454,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50067,0.02515,0.03315]},{"body_a":"attachment","body_b":"peg","contact_count":271.0,"contact_point_centroid":[0.5047,0.01504,0.04845],"force_p95":23.54506,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.87472,"mean_force":7.59804,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50081,0.02679,0.03331]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.50423,-0.02425,0.00982],"force_p95":18.09338,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.13881,"mean_force":6.11686,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50096,0.01924,0.03347]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.50636,-0.1003,0.03926],"force_p95":10.00303,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.75899,"mean_force":1.10469,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49841,-0.05215,0.04791]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52552,-0.08312,0.0114],"force_p95":12.15097,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.20889,"mean_force":5.96645,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50008,-0.05254,0.03313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":335.0,"contact_point_centroid":[0.50596,0.06209,0.0094],"force_p95":0.5542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.97275,"mean_force":0.62902,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51352,0.10438,0.07176]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50585,0.08023,0.04647],"force_p95":6.66802,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.68018,"mean_force":3.58719,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50524,0.09224,0.04126]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50862,-0.10013,0.06148],"force_p95":5.0575,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.0575,"mean_force":5.0575,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50066,-0.05144,0.03287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.50583,0.06299,0.00936],"force_p95":0.55996,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56645,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51164,0.15725,0.19898]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49991,0.19842,0.29649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":832.0,"contact_point_centroid":[0.50598,-0.08175,0.00941],"force_p95":0.59948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08646,"mean_force":0.54598,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49739,-0.05158,0.10236]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50377,-0.06433,0.05966],"force_p95":0.13655,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16046,"mean_force":0.07767,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49849,-0.0523,0.03752]}],"total_contact_groups":12},"final_pose_error":0.01178,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50614,-0.08193,0.03378],"final_tcp_position":[0.49776,-0.05154,0.17145],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":26.91178,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54573,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":714.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52441,0.11754,0.10706],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":335.0,"n_steps_budget":600.0,"object_pos_end":[0.50497,0.06042,0.03489],"object_pos_start":[0.50598,0.06294,0.03381],"object_to_goal_dist_end":0.1406,"object_to_goal_dist_start":0.1432,"object_z_max":0.03487,"peak_contact_force":0.43177,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":344.0,"raw_peak_contact_force":6.97275,"subtask_id":"pre_contact","tcp_end":[0.50425,0.09076,0.03754],"tcp_start":[0.52441,0.11754,0.10706],"tcp_to_object_dist_end":0.03046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.50864,-0.08183,0.03698],"object_pos_start":[0.50497,0.06042,0.03489],"object_to_goal_dist_end":0.00934,"object_to_goal_dist_start":0.1406,"object_z_max":0.03745,"peak_contact_force":5.10949,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":665.0,"raw_peak_contact_force":26.91178,"subtask_id":"push_complete","tcp_end":[0.50066,-0.05181,0.03287],"tcp_start":[0.50425,0.09076,0.03754],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.50614,-0.08193,0.03378],"object_pos_start":[0.50864,-0.08183,0.03698],"object_to_goal_dist_end":0.00895,"object_to_goal_dist_start":0.00934,"object_z_max":0.03698,"peak_contact_force":0.54973,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":929.0,"raw_peak_contact_force":12.75899,"tcp_end":[0.49776,-0.05154,0.17145],"tcp_start":[0.50066,-0.05181,0.03287],"tcp_to_object_dist_end":0.14124,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35922,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.01024,"push_1.push_distance":0.15914,"push_1.push_speed":0.09521},"optimized_scores":{"best_composite_score":0.33631,"best_fitness_score":0.54631,"best_task_score":0.21642},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52521,0.09405,0.05996],"force_p95":295.70121,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.07016,"mean_force":190.48894,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51334,0.09414,0.06087]},{"body_a":"attachment","body_b":"peg","contact_count":277.0,"contact_point_centroid":[0.49722,-0.06499,0.05469],"force_p95":23.4947,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.56828,"mean_force":16.04543,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49886,-0.05342,0.05447]},{"body_a":"attachment","body_b":"peg","contact_count":212.0,"contact_point_centroid":[0.50132,0.00153,0.04429],"force_p95":22.1208,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.51734,"mean_force":4.32928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50226,0.01283,0.03367]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":113.0,"contact_point_centroid":[0.47489,-0.05494,0.03517],"force_p95":23.07753,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.77102,"mean_force":5.23437,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5019,-0.02665,0.03309]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":146.0,"contact_point_centroid":[0.47488,-0.08188,0.05281],"force_p95":9.9198,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.70212,"mean_force":3.55648,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49892,-0.05366,0.04869]},{"body_a":"peg","body_b":"channel_base_body","contact_count":287.0,"contact_point_centroid":[0.49267,-0.1005,0.06151],"force_p95":23.456,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.37327,"mean_force":15.32095,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49887,-0.05345,0.05499]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52531,0.01167,0.04998],"force_p95":8.32762,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.62282,"mean_force":1.72063,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50204,0.04332,0.03343]},{"body_a":"peg","body_b":"channel_base_body","contact_count":168.0,"contact_point_centroid":[0.50066,-0.00965,0.00954],"force_p95":9.78744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.25121,"mean_force":2.66023,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50232,0.02354,0.03379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49289,-0.10068,0.04016],"force_p95":7.75062,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.92515,"mean_force":3.57003,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50209,-0.0543,0.03316]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50624,0.07345,0.04443],"force_p95":6.24992,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.44923,"mean_force":3.1531,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50593,0.0854,0.03957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.50643,0.05585,0.0094],"force_p95":0.55049,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.32457,"mean_force":0.60726,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51724,0.09826,0.07137]},{"body_a":"peg","body_b":"channel_base_body","contact_count":730.0,"contact_point_centroid":[0.50594,0.05664,0.00936],"force_p95":0.60012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56842,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51494,0.15415,0.19876]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49987,0.19836,0.29646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50628,-0.06387,0.00938],"force_p95":0.67272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.06382,"mean_force":0.5644,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49884,-0.05514,0.12585]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":73.0,"contact_point_centroid":[0.52508,-0.06307,0.05703],"force_p95":0.804,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13602,"mean_force":0.10967,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49873,-0.05507,0.12002]}],"total_contact_groups":15},"final_pose_error":0.01181,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50675,-0.06261,0.03387],"final_tcp_position":[0.49915,-0.0552,0.1717],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":297.07016,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05661,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54424,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":767.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53088,0.1115,0.10668],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":338.0,"n_steps_budget":600.0,"object_pos_end":[0.50505,0.05468,0.03472],"object_pos_start":[0.50615,0.05661,0.03378],"object_to_goal_dist_end":0.13488,"object_to_goal_dist_start":0.13689,"object_z_max":0.03472,"peak_contact_force":0.31449,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":360.0,"raw_peak_contact_force":297.07016,"subtask_id":"pre_contact","tcp_end":[0.50523,0.0846,0.03762],"tcp_start":[0.53088,0.1115,0.10668],"tcp_to_object_dist_end":0.03005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.49323,-0.08427,0.03473],"object_pos_start":[0.50505,0.05468,0.03472],"object_to_goal_dist_end":0.00958,"object_to_goal_dist_start":0.13488,"object_z_max":0.04048,"peak_contact_force":7.92515,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":530.0,"raw_peak_contact_force":29.51734,"subtask_id":"push_complete","tcp_end":[0.50206,-0.05549,0.03314],"tcp_start":[0.50523,0.0846,0.03762],"tcp_to_object_dist_end":0.03015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.50675,-0.06261,0.03387],"object_pos_start":[0.49323,-0.08427,0.03473],"object_to_goal_dist_end":0.01964,"object_to_goal_dist_start":0.00958,"object_z_max":0.05594,"peak_contact_force":0.54371,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1325.0,"raw_peak_contact_force":40.56828,"tcp_end":[0.49915,-0.0552,0.1717],"tcp_start":[0.50206,-0.05549,0.03314],"tcp_to_object_dist_end":0.13824,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```