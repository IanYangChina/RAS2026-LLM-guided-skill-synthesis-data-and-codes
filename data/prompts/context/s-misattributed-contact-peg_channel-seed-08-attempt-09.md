## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1931 | 0.43 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0281 | 0.46 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0915 | 0.47 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1052 | 0.52 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1028 | 0.52 | ✅ accepted |

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

## Current Skill (Q=0.193) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.1
  weight: 0.3
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_push
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    lateral_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_goal
- id: retract_tool
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_tool** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.193
- **task_score** (E): 0.426
- **fitness_score**: 0.486  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1787 |
| descend_to_contact | 1.00 | 1.00 | 0.1109 |
| push_to_goal | 0.67 | 1.00 | 0.0755 |
| retract_tool | 1.00 | 1.00 | 0.1195 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.115, 0.146) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.193 | 3.734 |
| descend_to_contact | descend | 1.00 / step_budget | (0.513, 0.115, 0.146)→(0.500, 0.109, 0.038) | (0.503, 0.080, 0.034)→(0.503, 0.079, 0.034) | 0.160→0.159 | 1.00 / 1.667 | 2610.827 | 7.820 |
| push_to_goal | push | 0.67 / force_exceeded | (0.500, 0.109, 0.038)→(0.499, 0.034, 0.032) | (0.503, 0.079, 0.034)→(0.506, 0.005, 0.036) | 0.159→0.086 | 1.00 / 1.667 | 0.450 | 10.291 |
| retract_tool | retract | 1.00 / step_budget | (0.499, 0.034, 0.032)→(0.496, -0.073, 0.082) | (0.506, 0.005, 0.036)→(0.502, -0.052, 0.033) | 0.086→0.030 | 1.00 / 1.000 | 0.540 | 3.526 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.842
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.737
- phase_score: 0.410
- phase_breakdown.pre_push_score: 0.125
- phase_breakdown.push_goal_score: 0.532

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.541
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.737
- **Median Q (composite search score)**: 0.224
- **K-run variance**: 0.0160
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.302


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37267,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.14158,"descend_to_contact.descend_speed":0.03372,"descend_to_contact.descend_tolerance":0.00857,"push_to_goal.force_threshold":39.1289,"push_to_goal.lateral_offset":0.01145,"push_to_goal.push_distance":0.14322,"push_to_goal.push_speed":0.04248,"retract_tool.retract_speed":0.10804},"optimized_scores":{"best_composite_score":0.33073,"best_fitness_score":0.54073,"best_task_score":0.73661},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":355.0,"contact_point_centroid":[0.49819,0.04339,0.03999],"force_p95":13.11376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.40713,"mean_force":6.00562,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49108,0.05295,0.03964]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":345.0,"contact_point_centroid":[0.52516,0.02944,0.0287],"force_p95":10.4024,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.32399,"mean_force":4.69905,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49112,0.05043,0.04046]},{"body_a":"peg","body_b":"channel_base_body","contact_count":850.0,"contact_point_centroid":[0.50146,-0.003,0.0088],"force_p95":9.48525,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.37907,"mean_force":2.60041,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49314,-0.00077,0.05798]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.475,-0.04001,0.02448],"force_p95":8.87678,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.92666,"mean_force":3.5178,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49536,-0.05361,0.07626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.50029,0.07355,0.00995],"force_p95":4.36387,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.14257,"mean_force":2.88483,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49061,0.11816,0.03153]},{"body_a":"attachment","body_b":"peg","contact_count":705.0,"contact_point_centroid":[0.49575,0.10532,0.04112],"force_p95":4.67597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.93653,"mean_force":2.47472,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49068,0.11666,0.03144]},{"body_a":"peg","body_b":"channel_base_body","contact_count":719.0,"contact_point_centroid":[0.49618,0.11697,0.0095],"force_p95":0.78405,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.01358,"mean_force":0.59877,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48678,0.14994,0.09027]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.49426,0.13656,0.05912],"force_p95":4.04086,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.63804,"mean_force":1.43489,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49082,0.14851,0.04407]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":195.0,"contact_point_centroid":[0.52505,0.07032,0.03007],"force_p95":2.86999,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.59494,"mean_force":1.44741,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49233,0.09637,0.03107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":427.0,"contact_point_centroid":[0.49625,0.1191,0.00941],"force_p95":0.63047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55845,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49138,0.17518,0.22049]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49947,0.19897,0.29754]}],"total_contact_groups":11},"final_pose_error":0.01064,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49383,-0.01572,0.02409],"final_tcp_position":[0.49621,-0.07295,0.08299],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3916.54146,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":452.0,"n_steps_budget":750.0,"object_pos_end":[0.49602,0.11915,0.03414],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.0254,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":757.0,"raw_peak_contact_force":5.01358,"subtask_id":"pre_push","tcp_end":[0.48456,0.15245,0.14894],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.49592,0.11845,0.0345],"object_pos_start":[0.49602,0.11915,0.03414],"object_to_goal_dist_end":0.19857,"object_to_goal_dist_start":0.19928,"object_z_max":0.03473,"peak_contact_force":3916.54146,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1555.0,"raw_peak_contact_force":7.14257,"subtask_id":"pre_push","tcp_end":[0.49154,0.14828,0.03617],"tcp_start":[0.48456,0.15245,0.14894],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":815.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,0.06199,0.03639],"object_pos_start":[0.49592,0.11845,0.0345],"object_to_goal_dist_end":0.14221,"object_to_goal_dist_start":0.19857,"object_z_max":0.03658,"peak_contact_force":0.49866,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1558.0,"raw_peak_contact_force":17.40713,"subtask_id":"push_goal","tcp_end":[0.493,0.08896,0.03099],"tcp_start":[0.49154,0.14828,0.03617],"tcp_to_object_dist_end":0.03086,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,-0.01572,0.02409],"object_pos_start":[0.507,0.06199,0.03639],"object_to_goal_dist_end":0.06651,"object_to_goal_dist_start":0.14221,"object_z_max":0.04081,"peak_contact_force":0.52833,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":451.0,"raw_peak_contact_force":2.24822,"subtask_id":"push_goal","tcp_end":[0.49621,-0.07295,0.08299],"tcp_start":[0.493,0.08896,0.03099],"tcp_to_object_dist_end":0.08216,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14124,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.09854,"descend_to_contact.descend_speed":0.02941,"descend_to_contact.descend_tolerance":0.00797,"push_to_goal.force_threshold":34.58786,"push_to_goal.lateral_offset":9e-05,"push_to_goal.push_distance":0.15473,"push_to_goal.push_speed":0.04952,"retract_tool.retract_speed":0.1764},"optimized_scores":{"best_composite_score":0.02504,"best_fitness_score":0.48504,"best_task_score":0.31554},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":904.0,"contact_point_centroid":[0.49904,0.0106,0.00993],"force_p95":3.19225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.34159,"mean_force":1.14991,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50037,0.05087,0.03271]},{"body_a":"attachment","body_b":"peg","contact_count":786.0,"contact_point_centroid":[0.50039,0.03759,0.03565],"force_p95":2.87813,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.09305,"mean_force":0.90979,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50034,0.04955,0.03263]},{"body_a":"attachment","body_b":"peg","contact_count":181.0,"contact_point_centroid":[0.50147,-0.02079,0.04202],"force_p95":5.07703,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.92842,"mean_force":1.91714,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49756,-0.00945,0.04069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":451.0,"contact_point_centroid":[0.50625,-0.05386,0.00997],"force_p95":4.08464,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.74307,"mean_force":1.20138,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49694,-0.03568,0.05711]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":86.0,"contact_point_centroid":[0.52503,-0.03913,0.02545],"force_p95":3.9116,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.21495,"mean_force":1.45246,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49701,-0.01489,0.0436]},{"body_a":"peg","body_b":"channel_base_body","contact_count":584.0,"contact_point_centroid":[0.50572,0.06295,0.00936],"force_p95":0.564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56973,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51188,0.14768,0.21817]},{"body_a":"peg","body_b":"channel_base_body","contact_count":555.0,"contact_point_centroid":[0.50582,0.06259,0.00938],"force_p95":0.55296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.38712,"mean_force":0.55811,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.513,0.09597,0.09109]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.5063,0.08092,0.0577],"force_p95":2.34117,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.01344,"mean_force":1.05197,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50405,0.093,0.04065]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5,0.1978,0.29645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.50584,-0.10009,0.03173],"force_p95":1.00705,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73947,"mean_force":0.32769,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49659,-0.05979,0.07245]}],"total_contact_groups":10},"final_pose_error":0.01159,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5053,-0.06972,0.03695],"final_tcp_position":[0.49655,-0.07328,0.08121],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":7.34159,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.02543,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":563.0,"raw_peak_contact_force":3.38712,"subtask_id":"pre_push","tcp_end":[0.52452,0.09951,0.14548],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.50588,0.06283,0.03413],"object_pos_start":[0.50596,0.06303,0.03381],"object_to_goal_dist_end":0.14307,"object_to_goal_dist_start":0.14329,"object_z_max":0.03411,"peak_contact_force":0.02552,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1690.0,"raw_peak_contact_force":7.34159,"subtask_id":"pre_push","tcp_end":[0.50361,0.09286,0.03809],"tcp_start":[0.52452,0.09951,0.14548],"tcp_to_object_dist_end":0.03038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5048,-0.01997,0.03529],"object_pos_start":[0.50588,0.06283,0.03413],"object_to_goal_dist_end":0.0604,"object_to_goal_dist_start":0.14307,"object_z_max":0.03536,"peak_contact_force":0.42792,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":889.0,"raw_peak_contact_force":6.92842,"subtask_id":"push_goal","tcp_end":[0.50078,0.00988,0.03172],"tcp_start":[0.50361,0.09286,0.03809],"tcp_to_object_dist_end":0.03033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.5053,-0.06972,0.03695],"object_pos_start":[0.5048,-0.01997,0.03529],"object_to_goal_dist_end":0.01196,"object_to_goal_dist_start":0.0604,"object_z_max":0.04079,"peak_contact_force":0.54713,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":618.0,"raw_peak_contact_force":3.88411,"subtask_id":"push_goal","tcp_end":[0.49655,-0.07328,0.08121],"tcp_start":[0.50078,0.00988,0.03172],"tcp_to_object_dist_end":0.04526,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18675,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.15892,"descend_to_contact.descend_speed":0.02593,"descend_to_contact.descend_tolerance":0.00691,"push_to_goal.force_threshold":33.13728,"push_to_goal.lateral_offset":0.00245,"push_to_goal.push_distance":0.16884,"push_to_goal.push_speed":0.06314,"retract_tool.retract_speed":0.15378},"optimized_scores":{"best_composite_score":0.22363,"best_fitness_score":0.43363,"best_task_score":0.22714},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":650.0,"contact_point_centroid":[0.50286,0.00304,0.00991],"force_p95":5.57045,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.97551,"mean_force":2.29133,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50153,0.04639,0.03301]},{"body_a":"attachment","body_b":"peg","contact_count":607.0,"contact_point_centroid":[0.50314,0.03096,0.0418],"force_p95":5.2752,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.61381,"mean_force":2.0202,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50156,0.04295,0.03287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":466.0,"contact_point_centroid":[0.50646,-0.05733,0.00997],"force_p95":3.32791,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.53818,"mean_force":1.04269,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49768,-0.03869,0.05693]},{"body_a":"attachment","body_b":"peg","contact_count":156.0,"contact_point_centroid":[0.50224,-0.02481,0.04038],"force_p95":4.27719,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.26383,"mean_force":1.56903,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49887,-0.01332,0.03986]},{"body_a":"peg","body_b":"channel_base_body","contact_count":551.0,"contact_point_centroid":[0.50587,0.05659,0.00935],"force_p95":0.60106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57538,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51538,0.14418,0.21745]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50023,0.1973,0.29578]},{"body_a":"peg","body_b":"channel_base_body","contact_count":545.0,"contact_point_centroid":[0.50605,0.05636,0.00938],"force_p95":0.55167,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.80244,"mean_force":0.55404,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51675,0.08971,0.09106]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50677,0.07456,0.05653],"force_p95":2.20344,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.55827,"mean_force":0.80604,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50478,0.08663,0.04019]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52501,-0.04463,0.02831],"force_p95":2.1248,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21855,"mean_force":0.62597,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49864,-0.0165,0.04189]},{"body_a":"peg","body_b":"channel_base_body","contact_count":188.0,"contact_point_centroid":[0.50662,-0.10007,0.03669],"force_p95":1.47029,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86882,"mean_force":0.36254,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49693,-0.06017,0.07169]}],"total_contact_groups":10},"final_pose_error":0.01129,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50663,-0.06926,0.03852],"final_tcp_position":[0.49665,-0.07375,0.08121],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":3915.91529,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":580.0,"n_steps_budget":810.0,"object_pos_end":[0.50611,0.05662,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52751,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":551.0,"raw_peak_contact_force":2.80244,"subtask_id":"pre_push","tcp_end":[0.53103,0.09328,0.14489],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,0.0565,0.03375],"object_pos_start":[0.50611,0.05662,0.03377],"object_to_goal_dist_end":0.13678,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":3915.91529,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1257.0,"raw_peak_contact_force":8.97551,"subtask_id":"pre_push","tcp_end":[0.50433,0.08652,0.03829],"tcp_start":[0.53103,0.09328,0.14489],"tcp_to_object_dist_end":0.03041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":813.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.02647,0.03543],"object_pos_start":[0.50618,0.0565,0.03375],"object_to_goal_dist_end":0.05418,"object_to_goal_dist_start":0.13678,"object_z_max":0.03541,"peak_contact_force":0.42337,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":835.0,"raw_peak_contact_force":6.53818,"subtask_id":"push_goal","tcp_end":[0.50228,0.00315,0.0318],"tcp_start":[0.50433,0.08652,0.03829],"tcp_to_object_dist_end":0.03021,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":518.0,"n_steps_budget":600.0,"object_pos_end":[0.50663,-0.06926,0.03852],"object_pos_start":[0.50701,-0.02647,0.03543],"object_to_goal_dist_end":0.01271,"object_to_goal_dist_start":0.05418,"object_z_max":0.04079,"peak_contact_force":0.54423,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":588.0,"raw_peak_contact_force":4.44541,"subtask_id":"push_goal","tcp_end":[0.49665,-0.07375,0.08121],"tcp_start":[0.50228,0.00315,0.0318],"tcp_to_object_dist_end":0.04408,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```