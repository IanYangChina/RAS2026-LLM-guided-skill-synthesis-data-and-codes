## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
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

## Current Skill (Q=-0.487) — your mutation base

```yaml
skill: peg_channel_new
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.02
  weight: 0.3
- id: push_complete
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.05
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
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
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
    pose_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_contact
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: add
    descend_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: add
    pose_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_contact
- id: contact_peg
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
    - 0.01
    - 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    contact_offset_y:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.y
        mode: add
    contact_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: add
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_contact
- id: push_phase
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    pose_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: add
    retry_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: add
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_complete
- id: retract_tcp
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
    - 0.05
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (add)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - descend_offset_z: status=consumed; consumers=target.offset.z (add)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.005]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - contact_offset_y: status=consumed; consumers=target.offset.y (add)
    - contact_offset_z: status=consumed; consumers=target.offset.z (add)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_phase** (`push`)
  - target: source=yaml, anchor=task_goal, entity=peg, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (add)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (add)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract_tcp** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.487
- **task_score** (E): 0.226
- **fitness_score**: 0.337  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.890

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.0309 |
| descend_to_peg | 1.00 | 1.00 | 0.1680 |
| contact_peg | 0.33 | 1.00 | 0.0989 |
| push_phase | 0.00 | 1.00 | 0.0004 |
| retract_tcp | 1.00 | 1.00 | 0.0408 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.488, 0.188, 0.277) | (0.494, 0.068, 0.040)→(0.503, 0.068, 0.035) | 0.151→0.148 | 1.00 / 1.000 | 0.411 | 3.453 |
| descend_to_peg | descend | 1.00 / step_budget | (0.488, 0.188, 0.277)→(0.503, 0.178, 0.110) | (0.503, 0.068, 0.035)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.546 | 1.834 |
| contact_peg | contact | 0.33 / step_budget | (0.503, 0.178, 0.110)→(0.498, 0.101, 0.049) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.333 | 3.934 | 3.940 |
| push_phase | push | 0.00 / guard_failure | (0.496, -0.020, 0.039)→(0.496, -0.020, 0.039) | (0.498, 0.068, 0.034)→(0.499, -0.033, 0.032) | 0.148→0.051 | 1.00 / 2.333 | 14.166 | 46.191 |
| retract_tcp | retract | 1.00 / step_budget | (0.496, -0.020, 0.039)→(0.493, -0.020, 0.080) | (0.499, -0.033, 0.033)→(0.497, -0.029, 0.032) | 0.051→0.052 | 1.00 / 1.000 | 0.546 | 19.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.613
- alignment_error: None
- force_efficiency: 0.195
- terminal_score: 0.361
- phase_score: 0.325
- phase_breakdown.push_complete_score: 0.185
- phase_breakdown.reach_contact_score: 0.650

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.425
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.361
- **Median Q (composite search score)**: -0.465
- **K-run variance**: 0.0146
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.261


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57857,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":-0.01503,"approach_peg.approach_offset_y":0.05986,"approach_peg.approach_offset_z":0.10073,"approach_peg.pose_tolerance":0.02259,"contact_peg.approach_offset_x":0.00614,"contact_peg.contact_offset_y":0.0146,"contact_peg.contact_offset_z":0.00669,"contact_peg.force_threshold":9.63791,"descend_to_peg.approach_offset_x":-0.00433,"descend_to_peg.approach_offset_y":0.05733,"descend_to_peg.descend_offset_z":0.0236,"descend_to_peg.pose_tolerance":0.03726,"push_phase.pose_tolerance":0.03086,"push_phase.push_speed":0.06839,"push_phase.retry_offset_x":0.00445,"push_phase.retry_offset_y":0.00159},"optimized_scores":{"best_composite_score":-0.35059,"best_fitness_score":0.33941,"best_task_score":0.3612},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":68.0,"contact_point_centroid":[0.49349,0.0055,0.00942],"force_p95":27.07737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.25408,"mean_force":7.16161,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49545,0.04655,0.04075]},{"body_a":"attachment","body_b":"peg","contact_count":91.0,"contact_point_centroid":[0.49518,0.04483,0.04468],"force_p95":25.54708,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.39259,"mean_force":4.97735,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49529,0.05661,0.04116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":657.0,"contact_point_centroid":[0.49525,0.06373,0.0094],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.71426,"mean_force":0.57934,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48981,0.13314,0.07784]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49605,0.08155,0.04559],"force_p95":9.6895,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.099,"mean_force":3.98659,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49651,0.0934,0.04555]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49427,-0.00808,0.03838],"force_p95":2.20852,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.98686,"mean_force":0.75475,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49521,0.00346,0.03819]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47484,0.0346,0.03093],"force_p95":1.34634,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.65286,"mean_force":0.75063,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49537,0.06415,0.04181]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.49724,0.06427,0.00921],"force_p95":1.45278,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.67291,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48592,0.18936,0.27394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.4967,-0.03443,0.00934],"force_p95":0.62739,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.34641,"mean_force":0.57353,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49211,0.004,0.06023]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.4743,-0.02751,0.03096],"force_p95":1.03292,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29009,"mean_force":0.46481,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49452,0.00332,0.0391]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49761,0.19806,0.29593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":172.0,"contact_point_centroid":[0.49503,0.06366,0.00939],"force_p95":0.5601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58098,"mean_force":0.54568,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48142,0.17797,0.18868]}],"total_contact_groups":11},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49651,-0.03419,0.03378],"final_tcp_position":[0.49201,0.00408,0.07888],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":40.25408,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.49513,0.06371,0.03386],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14393,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.58357,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":94.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.47703,0.18268,0.25791],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.49519,0.06374,0.0339],"object_pos_start":[0.49513,0.06371,0.03386],"object_to_goal_dist_end":0.14395,"object_to_goal_dist_start":0.14393,"object_z_max":0.0339,"peak_contact_force":0.54489,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":172.0,"raw_peak_contact_force":0.58098,"subtask_id":"reach_contact","tcp_end":[0.48639,0.17304,0.11432],"tcp_start":[0.47703,0.18268,0.25791],"tcp_to_object_dist_end":0.13598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":657.0,"n_steps_budget":720.0,"object_pos_end":[0.49495,0.06337,0.03405],"object_pos_start":[0.49519,0.06374,0.0339],"object_to_goal_dist_end":0.14358,"object_to_goal_dist_start":0.14395,"object_z_max":0.034,"peak_contact_force":10.71426,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":663.0,"raw_peak_contact_force":10.71426,"subtask_id":"reach_contact","tcp_end":[0.49657,0.09303,0.04525],"tcp_start":[0.48639,0.17304,0.11432],"tcp_to_object_dist_end":0.03175,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.49381,-0.02403,0.03623],"object_pos_start":[0.49495,0.06337,0.03405],"object_to_goal_dist_end":0.05644,"object_to_goal_dist_start":0.14358,"object_z_max":0.03916,"peak_contact_force":1.55817,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":182.0,"raw_peak_contact_force":40.25408,"subtask_id":"push_complete","tcp_end":[0.49555,0.00412,0.03822],"tcp_start":[0.49556,0.00448,0.03825],"tcp_to_object_dist_end":0.02828,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":394.0,"n_steps_budget":600.0,"object_pos_end":[0.49651,-0.03419,0.03378],"object_pos_start":[0.49343,-0.02463,0.03735],"object_to_goal_dist_end":0.04636,"object_to_goal_dist_start":0.05582,"object_z_max":0.04035,"peak_contact_force":0.54897,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":399.0,"raw_peak_contact_force":2.98686,"tcp_end":[0.49201,0.00408,0.07888],"tcp_start":[0.49555,0.00412,0.03822],"tcp_to_object_dist_end":0.05932,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28481,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00375,"approach_peg.approach_offset_y":0.06344,"approach_peg.approach_offset_z":0.12686,"approach_peg.pose_tolerance":0.01764,"contact_peg.approach_offset_x":0.00456,"contact_peg.contact_offset_y":0.02173,"contact_peg.contact_offset_z":0.01954,"contact_peg.force_threshold":14.49275,"descend_to_peg.approach_offset_x":0.01435,"descend_to_peg.approach_offset_y":0.05416,"descend_to_peg.descend_offset_z":0.02813,"descend_to_peg.pose_tolerance":0.02648,"push_phase.pose_tolerance":0.03882,"push_phase.push_speed":0.05404,"push_phase.retry_offset_x":0.00089,"push_phase.retry_offset_y":-0.00503},"optimized_scores":{"best_composite_score":-0.64397,"best_fitness_score":0.24603,"best_task_score":0.10692},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":113.0,"contact_point_centroid":[0.49523,0.02034,0.00823],"force_p95":16.97745,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.70949,"mean_force":2.70239,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49483,0.04215,0.04874]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49663,0.04406,0.05014],"force_p95":43.58789,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.19757,"mean_force":13.48361,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49459,0.05232,0.04995]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.49412,0.00676,0.0081],"force_p95":0.87687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.24886,"mean_force":1.07923,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.4925,-0.00989,0.06279]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.49985,-0.01473,0.04235],"force_p95":21.50466,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.96352,"mean_force":8.51254,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49506,-0.01085,0.04298]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47498,0.0325,0.0242],"force_p95":9.38008,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.44041,"mean_force":3.37096,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49233,-0.00984,0.05445]},{"body_a":"peg","body_b":"channel_base_body","contact_count":53.0,"contact_point_centroid":[0.49692,0.05957,0.00907],"force_p95":2.56944,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.82276,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48762,0.18891,0.28427]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49684,0.19715,0.29617]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.02492,0.06],"force_p95":1.39959,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39959,"mean_force":1.39959,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.4942,0.07357,0.05247]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.49417,0.05899,0.00938],"force_p95":0.55601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5959,"mean_force":0.54607,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49075,0.17415,0.19298]},{"body_a":"peg","body_b":"channel_base_body","contact_count":534.0,"contact_point_centroid":[0.49418,0.05885,0.00939],"force_p95":0.55038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54613,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.497,0.12996,0.07969]}],"total_contact_groups":10},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49371,0.00791,0.02405],"final_tcp_position":[0.49218,-0.00967,0.08315],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":51.70949,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":82.0,"n_steps_budget":600.0,"object_pos_end":[0.49411,0.05898,0.03371],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13925,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.49931,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":88.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.48086,0.18274,0.27603],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05898,0.03385],"object_pos_start":[0.49411,0.05898,0.03371],"object_to_goal_dist_end":0.13925,"object_to_goal_dist_start":0.13925,"object_z_max":0.03385,"peak_contact_force":0.54521,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":268.0,"raw_peak_contact_force":0.5959,"subtask_id":"reach_contact","tcp_end":[0.50191,0.16533,0.10677],"tcp_start":[0.48086,0.18274,0.27603],"tcp_to_object_dist_end":0.12919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.49416,0.05912,0.03391],"object_pos_start":[0.49403,0.05898,0.03385],"object_to_goal_dist_end":0.13938,"object_to_goal_dist_start":0.13925,"object_z_max":0.03391,"peak_contact_force":0.54463,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":534.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_contact","tcp_end":[0.4951,0.09519,0.05705],"tcp_start":[0.50191,0.16533,0.10677],"tcp_to_object_dist_end":0.04286,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.49759,0.0077,0.02428],"object_pos_start":[0.49416,0.05912,0.03391],"object_to_goal_dist_end":0.08913,"object_to_goal_dist_start":0.13938,"object_z_max":0.04214,"peak_contact_force":38.46133,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":131.0,"raw_peak_contact_force":51.70949,"subtask_id":"push_complete","tcp_end":[0.49569,-0.00972,0.0425],"tcp_start":[0.49571,-0.00921,0.04254],"tcp_to_object_dist_end":0.02528,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":600.0,"object_pos_end":[0.49371,0.00791,0.02405],"object_pos_start":[0.49754,0.00756,0.02446],"object_to_goal_dist_end":0.08957,"object_to_goal_dist_start":0.08896,"object_z_max":0.02579,"peak_contact_force":0.67393,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":417.0,"raw_peak_contact_force":33.24886,"tcp_end":[0.49218,-0.00967,0.08315],"tcp_start":[0.49569,-0.00972,0.0425],"tcp_to_object_dist_end":0.06168,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62963,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00086,"approach_peg.approach_offset_y":0.05088,"approach_peg.approach_offset_z":0.14505,"approach_peg.pose_tolerance":0.03715,"contact_peg.approach_offset_x":0.00085,"contact_peg.contact_offset_y":0.01854,"contact_peg.contact_offset_z":0.00818,"contact_peg.force_threshold":22.43554,"descend_to_peg.approach_offset_x":0.00677,"descend_to_peg.approach_offset_y":0.06406,"descend_to_peg.descend_offset_z":0.02125,"descend_to_peg.pose_tolerance":0.03032,"push_phase.pose_tolerance":0.02328,"push_phase.push_speed":0.07732,"push_phase.retry_offset_x":0.0038,"push_phase.retry_offset_y":0.00139},"optimized_scores":{"best_composite_score":-0.46515,"best_fitness_score":0.42485,"best_task_score":0.21081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50548,-0.10045,0.0606],"force_p95":45.82388,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.61063,"mean_force":32.10348,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49706,-0.05396,0.03606]},{"body_a":"attachment","body_b":"peg","contact_count":263.0,"contact_point_centroid":[0.50321,0.01462,0.05104],"force_p95":29.02951,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.37191,"mean_force":7.89577,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49883,0.02608,0.03886]},{"body_a":"peg","body_b":"channel_base_body","contact_count":116.0,"contact_point_centroid":[0.506,0.0002,0.00975],"force_p95":29.14533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.35421,"mean_force":8.21755,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49951,0.04179,0.03986]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":260.0,"contact_point_centroid":[0.5253,0.00556,0.02936],"force_p95":27.29923,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.15643,"mean_force":4.98027,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49903,0.03392,0.03918]},{"body_a":"peg","body_b":"channel_base_body","contact_count":367.0,"contact_point_centroid":[0.50719,-0.10025,0.06372],"force_p95":16.06002,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.78843,"mean_force":6.79968,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49335,-0.05365,0.05215]},{"body_a":"attachment","body_b":"peg","contact_count":362.0,"contact_point_centroid":[0.49769,-0.06467,0.05216],"force_p95":16.31327,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.56842,"mean_force":6.98549,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49335,-0.05364,0.05192]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.50313,-0.06817,0.00916],"force_p95":2.65308,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.29987,"mean_force":1.00804,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49366,-0.05429,0.06714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.50544,0.08086,0.00933],"force_p95":0.62882,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60804,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51302,0.19568,0.20142]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.53608,0.0809,0.03623],"force_p95":1.42345,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.74342,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50126,0.19911,0.29916]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.5278,0.0809,0.01432],"force_p95":0.85693,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98339,"mean_force":0.24396,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50575,0.19679,0.29337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":622.0,"contact_point_centroid":[0.50595,0.08092,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55048,"mean_force":0.54677,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51079,0.15355,0.0749]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,-0.08044,0.05999],"force_p95":0.3882,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39449,"mean_force":0.33522,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49319,-0.05398,0.07034]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47498,-0.07462,0.02928],"force_p95":0.25156,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26002,"mean_force":0.18254,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49298,-0.05353,0.06234]}],"total_contact_groups":13},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50196,-0.05925,0.03805],"final_tcp_position":[0.49334,-0.05427,0.07668],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":46.61063,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.51972,0.08091,0.03863],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16212,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.15096,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":3.70803,"subtask_id":"reach_contact","tcp_end":[0.5051,0.19765,0.297],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.51972,0.08091,0.03863],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16212,"object_z_max":0.03863,"peak_contact_force":0.54772,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":265.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.52098,0.19447,0.10934],"tcp_start":[0.5051,0.19765,0.297],"tcp_to_object_dist_end":0.13726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":622.0,"n_steps_budget":690.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":622.0,"raw_peak_contact_force":0.55048,"subtask_id":"reach_contact","tcp_end":[0.50381,0.11364,0.04575],"tcp_start":[0.52098,0.19447,0.10934],"tcp_to_object_dist_end":0.03496,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,-0.08184,0.03653],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.0072,"object_to_goal_dist_start":0.1611,"object_z_max":0.03763,"peak_contact_force":2.4775,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":643.0,"raw_peak_contact_force":46.61063,"subtask_id":"push_complete","tcp_end":[0.49693,-0.05473,0.03593],"tcp_start":[0.497,-0.0545,0.036],"tcp_to_object_dist_end":0.02861,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":441.0,"n_steps_budget":600.0,"object_pos_end":[0.50196,-0.05925,0.03805],"object_pos_start":[0.50581,-0.0825,0.03637],"object_to_goal_dist_end":0.02093,"object_to_goal_dist_start":0.0073,"object_z_max":0.04962,"peak_contact_force":0.41463,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":801.0,"raw_peak_contact_force":20.78843,"tcp_end":[0.49334,-0.05427,0.07668],"tcp_start":[0.49693,-0.05473,0.03593],"tcp_to_object_dist_end":0.03989,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```