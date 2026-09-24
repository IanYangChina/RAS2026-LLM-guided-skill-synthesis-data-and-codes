## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.3779 | 0.00 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 7  | -0.4752 | 0.00 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.0545 | 0.25 | ✅ accepted |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.2368 | 0.13 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.0495 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=-0.049) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: push_through_channel
  metric: goal_progress
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.174
  parameters:
    approach_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: add
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
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
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset_y:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: add
    descend_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.174
  parameters:
    push_max_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: push_through_channel
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
    retract_speed:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.08], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.174
  - parameter_bindings:
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (add)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_y: status=consumed; consumers=target.offset.y (add)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.174
  - parameter_bindings:
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (add)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.049
- **task_score** (E): 0.254
- **fitness_score**: 0.461  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0690 |
| descend_1 | 1.00 | 1.00 | 0.2026 |
| push_1 | 1.00 | 1.00 | 0.1278 |
| retract_1 | 1.00 | 1.00 | 0.2311 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.504, 0.192, 0.236) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.541 | 3.954 |
| descend_1 | descend | 1.00 / step_budget | (0.504, 0.192, 0.236)→(0.499, 0.135, 0.042) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.546 | 0.564 |
| push_1 | push | 1.00 / time_limit | (0.499, 0.135, 0.042)→(0.495, 0.007, 0.037) | (0.502, 0.082, 0.034)→(0.508, -0.022, 0.037) | 0.162→0.059 | 1.00 / 2.333 | 25.447 | 33.443 |
| retract_1 | retract | 1.00 / step_budget | (0.495, 0.007, 0.037)→(0.494, 0.013, 0.268) | (0.508, -0.022, 0.037)→(0.504, -0.029, 0.031) | 0.059→0.053 | 1.00 / 1.000 | 0.612 | 19.675 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.666
- alignment_error: None
- force_efficiency: 0.805
- terminal_score: 0.352
- phase_score: 0.558
- phase_breakdown.push_through_channel_score: 0.570
- phase_breakdown.reach_peg_score: 0.529

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.475
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.352
- **Median Q (composite search score)**: -0.040
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.431


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.288,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.07892,"approach_1.approach_offset_z":0.0934,"approach_1.approach_speed":0.31233,"descend_1.descend_offset_y":0.02002,"descend_1.descend_speed":0.09046,"push_1.push_max_time":4.90433,"push_1.push_speed":0.07846,"retract_1.retract_height":0.16246,"retract_1.retract_speed":0.67589},"optimized_scores":{"best_composite_score":-0.03959,"best_fitness_score":0.47041,"best_task_score":0.20655},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":723.0,"contact_point_centroid":[0.49713,0.02622,0.03924],"force_p95":67.48949,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.6721,"mean_force":28.21249,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48951,0.03509,0.03647]},{"body_a":"peg","body_b":"channel_base_body","contact_count":916.0,"contact_point_centroid":[0.50431,0.0143,0.00972],"force_p95":40.04808,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.55072,"mean_force":13.90551,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48895,0.04999,0.03678]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.4988,-0.01577,0.0355],"force_p95":33.22823,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.05859,"mean_force":6.3963,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49034,-0.00849,0.03652]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":607.0,"contact_point_centroid":[0.52553,0.00779,0.02795],"force_p95":49.82577,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.71831,"mean_force":23.74621,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48987,0.0272,0.03641]},{"body_a":"peg","body_b":"channel_base_body","contact_count":532.0,"contact_point_centroid":[0.5005,-0.05532,0.00858],"force_p95":1.17897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.84992,"mean_force":0.76665,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4894,0.01209,0.17821]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":53.0,"contact_point_centroid":[0.52537,-0.03149,0.02697],"force_p95":5.36376,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.66223,"mean_force":1.54308,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48921,0.00035,0.06529]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.475,0.10304,0.03962],"force_p95":26.29047,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":28.6975,"mean_force":18.78748,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,0.10303,0.03769]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47497,-0.08073,0.0275],"force_p95":5.66765,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.75085,"mean_force":2.10206,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48947,0.01236,0.20546]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.49513,0.059,0.00923],"force_p95":1.22261,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.6764,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48587,0.19147,0.25966]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49757,0.19873,0.29383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":674.0,"contact_point_centroid":[0.4942,0.05902,0.00939],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55479,"mean_force":0.54623,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48093,0.15086,0.13527]}],"total_contact_groups":11},"final_pose_error":0.02474,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49761,-0.06087,0.02413],"final_tcp_position":[0.49049,-0.00223,0.32466],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":77.6721,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":141.0,"n_steps_budget":600.0,"object_pos_end":[0.49413,0.05891,0.0338],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13917,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54251,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":147.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.47457,0.18865,0.23136],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.23716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.49398,0.05902,0.0339],"object_pos_start":[0.49413,0.05891,0.0338],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.13917,"object_z_max":0.0339,"peak_contact_force":0.54506,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":674.0,"raw_peak_contact_force":0.55479,"subtask_id":"reach_peg","tcp_end":[0.48929,0.11305,0.04142],"tcp_start":[0.47457,0.18865,0.23136],"tcp_to_object_dist_end":0.05476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50897,-0.03943,0.03957],"object_pos_start":[0.49398,0.05902,0.0339],"object_to_goal_dist_end":0.04156,"object_to_goal_dist_start":0.13928,"object_z_max":0.04032,"peak_contact_force":75.10245,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2275.0,"raw_peak_contact_force":77.6721,"subtask_id":"push_through_channel","tcp_end":[0.49137,-0.00871,0.03607],"tcp_start":[0.48929,0.11305,0.04142],"tcp_to_object_dist_end":0.03558,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49761,-0.06087,0.02413],"object_pos_start":[0.50897,-0.03943,0.03957],"object_to_goal_dist_end":0.02497,"object_to_goal_dist_start":0.04156,"object_z_max":0.04059,"peak_contact_force":0.74192,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":603.0,"raw_peak_contact_force":57.05859,"tcp_end":[0.49049,-0.00223,0.32466],"tcp_start":[0.49137,-0.00871,0.03607],"tcp_to_object_dist_end":0.30628,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78146,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.06277,"approach_1.approach_offset_z":0.11565,"approach_1.approach_speed":0.31497,"descend_1.descend_offset_y":0.02004,"descend_1.descend_speed":0.06204,"push_1.push_max_time":5.9633,"push_1.push_speed":0.07972,"retract_1.retract_height":0.09286,"retract_1.retract_speed":0.72688},"optimized_scores":{"best_composite_score":-0.07423,"best_fitness_score":0.43577,"best_task_score":0.20252},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":668.0,"contact_point_centroid":[0.50239,0.04585,0.04327],"force_p95":7.34009,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.91736,"mean_force":2.68713,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49833,0.0574,0.03714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.50627,0.03072,0.00977],"force_p95":7.37049,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.38997,"mean_force":3.0614,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49882,0.07511,0.03758]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":405.0,"contact_point_centroid":[0.52504,0.02663,0.02036],"force_p95":2.85356,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.57322,"mean_force":0.8839,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49829,0.0546,0.03712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":94.0,"contact_point_centroid":[0.50437,0.08071,0.00925],"force_p95":1.78197,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.70916,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51181,0.20065,0.26979]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50174,0.20077,0.29453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":530.0,"contact_point_centroid":[0.50655,-0.02467,0.00942],"force_p95":0.61714,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95402,"mean_force":0.54926,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49516,0.02,0.14649]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52506,-0.02408,0.0553],"force_p95":0.26428,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70132,"mean_force":0.11734,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49529,0.01035,0.05416]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50181,-0.00769,0.04099],"force_p95":0.59429,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.637,"mean_force":0.28231,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49747,0.0037,0.03657]},{"body_a":"peg","body_b":"channel_base_body","contact_count":681.0,"contact_point_centroid":[0.50598,0.08093,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55543,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51197,0.16549,0.14494]}],"total_contact_groups":9},"final_pose_error":0.02062,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50686,-0.02445,0.03378],"final_tcp_position":[0.49588,0.00894,0.25955],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":12.91736,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":123.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.53988,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":130.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52231,0.19696,0.24998],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":681.0,"raw_peak_contact_force":0.55543,"subtask_id":"reach_peg","tcp_end":[0.50331,0.13419,0.04265],"tcp_start":[0.52231,0.19696,0.24998],"tcp_to_object_dist_end":0.05412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50711,-0.0244,0.03603],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.05619,"object_to_goal_dist_start":0.1611,"object_z_max":0.03613,"peak_contact_force":0.89846,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1734.0,"raw_peak_contact_force":12.91736,"subtask_id":"push_through_channel","tcp_end":[0.49753,0.0038,0.03659],"tcp_start":[0.50331,0.13419,0.04265],"tcp_to_object_dist_end":0.02979,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":533.0,"n_steps_budget":600.0,"object_pos_end":[0.50686,-0.02445,0.03378],"object_pos_start":[0.50711,-0.0244,0.03603],"object_to_goal_dist_end":0.05632,"object_to_goal_dist_start":0.05619,"object_z_max":0.03603,"peak_contact_force":0.54922,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":564.0,"raw_peak_contact_force":0.95402,"tcp_end":[0.49588,0.00894,0.25955],"tcp_start":[0.49753,0.0038,0.03659],"tcp_to_object_dist_end":0.22849,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61842,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.03084,"approach_1.approach_offset_z":0.08775,"approach_1.approach_speed":0.79982,"descend_1.descend_offset_y":0.02216,"descend_1.descend_speed":0.05209,"push_1.push_max_time":9.60076,"push_1.push_speed":0.0799,"retract_1.retract_height":0.05064,"retract_1.retract_speed":0.40043},"optimized_scores":{"best_composite_score":-0.03467,"best_fitness_score":0.47533,"best_task_score":0.35171},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":681.0,"contact_point_centroid":[0.50224,0.06938,0.04234],"force_p95":7.37921,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.74072,"mean_force":2.67914,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49823,0.08089,0.03742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.50656,0.05531,0.00978],"force_p95":7.52219,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.47666,"mean_force":3.05598,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49867,0.09969,0.03787]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":443.0,"contact_point_centroid":[0.52505,0.05264,0.02254],"force_p95":3.06683,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.7869,"mean_force":0.97687,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49823,0.08062,0.03742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.50508,0.10468,0.00932],"force_p95":0.96788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.63254,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50768,0.19618,0.25737]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50055,0.20022,0.29461]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.50647,-0.00207,0.00942],"force_p95":0.59791,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01324,"mean_force":0.55051,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49508,0.04069,0.12745]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52504,-0.00104,0.03761],"force_p95":0.52605,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67463,"mean_force":0.17176,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49616,0.03132,0.04789]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5024,0.01569,0.04809],"force_p95":0.59695,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.6389,"mean_force":0.312,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49751,0.0272,0.03684]},{"body_a":"peg","body_b":"channel_base_body","contact_count":594.0,"contact_point_centroid":[0.50579,0.10468,0.00939],"force_p95":0.57547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58307,"mean_force":0.54639,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50874,0.17341,0.13328]}],"total_contact_groups":9},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50662,-0.00199,0.03392],"final_tcp_position":[0.49553,0.03197,0.21842],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":9.74072,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.50591,0.10458,0.03382],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53949,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":163.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51623,0.18911,0.2252],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.50591,0.10458,0.03382],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.54908,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":594.0,"raw_peak_contact_force":0.58307,"subtask_id":"reach_peg","tcp_end":[0.50301,0.15802,0.04302],"tcp_start":[0.51623,0.18911,0.2252],"tcp_to_object_dist_end":0.05421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50691,-0.00092,0.03598],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.07949,"object_to_goal_dist_start":0.18488,"object_z_max":0.03617,"peak_contact_force":0.33928,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1785.0,"raw_peak_contact_force":9.74072,"subtask_id":"push_through_channel","tcp_end":[0.49755,0.02731,0.03685],"tcp_start":[0.50301,0.15802,0.04302],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":470.0,"n_steps_budget":600.0,"object_pos_end":[0.50662,-0.00199,0.03392],"object_pos_start":[0.50691,-0.00092,0.03598],"object_to_goal_dist_end":0.07852,"object_to_goal_dist_start":0.07949,"object_z_max":0.03599,"peak_contact_force":0.54395,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":476.0,"raw_peak_contact_force":1.01324,"tcp_end":[0.49553,0.03197,0.21842],"tcp_start":[0.49755,0.02731,0.03685],"tcp_to_object_dist_end":0.18793,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```