## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

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

## Current Skill (Q=-0.746) — your mutation base

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
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.026
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.026], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (add)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (add)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract_tcp** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.746
- **task_score** (E): 0.002
- **fitness_score**: 0.110  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.940

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.0642 |
| descend_to_peg | 1.00 | 1.00 | 0.1296 |
| contact_peg | 0.33 | 1.00 | 0.0974 |
| push_phase | 0.00 | 1.00 | 0.0219 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.187, 0.240) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.553 | 3.659 |
| descend_to_peg | descend | 1.00 / step_budget | (0.499, 0.187, 0.240)→(0.498, 0.191, 0.111) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.545 | 0.588 |
| contact_peg | contact | 0.33 / step_budget | (0.498, 0.191, 0.111)→(0.499, 0.116, 0.050) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.333 | 18.148 | 18.155 |
| push_phase | push | 0.00 / guard_failure | (0.499, 0.116, 0.050)→(0.511, 0.103, 0.038) | (0.498, 0.068, 0.034)→(0.498, 0.067, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 182.448 | 660.935 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.179
- phase_breakdown.push_complete_score: 0.000
- phase_breakdown.reach_contact_score: 0.595

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.130
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.006
- **Median Q (composite search score)**: -0.810
- **K-run variance**: 0.0135
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.259


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":-0.0042,"approach_peg.approach_offset_y":0.05627,"approach_peg.approach_offset_z":0.0884,"approach_peg.pose_tolerance":0.03905,"contact_peg.approach_offset_x":-0.00419,"contact_peg.contact_offset_y":0.0152,"contact_peg.contact_offset_z":0.0114,"contact_peg.force_threshold":15.10994,"descend_to_peg.approach_offset_x":-0.00104,"descend_to_peg.approach_offset_y":0.07203,"descend_to_peg.descend_offset_z":0.02434,"descend_to_peg.pose_tolerance":0.04323,"push_phase.max_time":6.46242,"push_phase.push_distance":0.15647,"push_phase.push_speed":0.05524,"push_phase.retry_offset_x":0.0027,"push_phase.retry_offset_y":-0.00066},"optimized_scores":{"best_composite_score":-0.81029,"best_fitness_score":0.12971,"best_task_score":0.00627},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50088,0.08045,0.03812],"force_p95":54.66458,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.7197,"mean_force":36.16855,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50458,0.09147,0.03622]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50148,0.06755,0.0094],"force_p95":22.8539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.88071,"mean_force":4.71017,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49541,0.10028,0.04443]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.49933,0.06536,0.00913],"force_p95":1.70951,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.73366,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49145,0.18887,0.26381]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49846,0.19782,0.29358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.49534,0.06359,0.00938],"force_p95":0.58227,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61238,"mean_force":0.54512,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48868,0.18642,0.18465]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.49493,0.06382,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54566,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48747,0.14991,0.08277]}],"total_contact_groups":6},"final_pose_error":0.1419,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49458,0.06233,0.03414],"final_tcp_position":[0.50568,0.09015,0.03351],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":56.7197,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":72.0,"n_steps_budget":630.0,"object_pos_end":[0.49496,0.06375,0.03377],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14397,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.62821,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":73.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.48654,0.18264,0.24386],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":131.0,"n_steps_budget":1000.0,"object_pos_end":[0.49502,0.064,0.03389],"object_pos_start":[0.49496,0.06375,0.03377],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14397,"object_z_max":0.03389,"peak_contact_force":0.5409,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":131.0,"raw_peak_contact_force":0.61238,"subtask_id":"reach_contact","tcp_end":[0.49108,0.19136,0.12032],"tcp_start":[0.48654,0.18264,0.24386],"tcp_to_object_dist_end":0.15396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.49518,0.06363,0.034],"object_pos_start":[0.49502,0.064,0.03389],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14422,"object_z_max":0.034,"peak_contact_force":0.5415,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":662.0,"raw_peak_contact_force":0.55295,"subtask_id":"reach_contact","tcp_end":[0.48712,0.1084,0.04971],"tcp_start":[0.49108,0.19136,0.12032],"tcp_to_object_dist_end":0.04813,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.49458,0.06233,0.03414],"object_pos_start":[0.49518,0.06363,0.034],"object_to_goal_dist_end":0.14256,"object_to_goal_dist_start":0.14384,"object_z_max":0.034,"peak_contact_force":0.02508,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":56.7197,"subtask_id":"push_complete","tcp_end":[0.50568,0.09015,0.03351],"tcp_start":[0.48712,0.1084,0.04971],"tcp_to_object_dist_end":0.02996,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95122,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.01012,"approach_peg.approach_offset_y":0.05531,"approach_peg.approach_offset_z":0.095,"approach_peg.pose_tolerance":0.03776,"contact_peg.approach_offset_x":-0.0023,"contact_peg.contact_offset_y":0.01948,"contact_peg.contact_offset_z":0.00732,"contact_peg.force_threshold":14.19787,"descend_to_peg.approach_offset_x":0.00391,"descend_to_peg.approach_offset_y":0.07188,"descend_to_peg.descend_offset_z":0.02367,"descend_to_peg.pose_tolerance":0.02924,"push_phase.max_time":9.56891,"push_phase.push_distance":0.14976,"push_phase.push_speed":0.06691,"push_phase.retry_offset_x":0.00282,"push_phase.retry_offset_y":-0.00187},"optimized_scores":{"best_composite_score":-0.84535,"best_fitness_score":0.09465,"best_task_score":0.00032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53873,0.11045,0.05992],"force_p95":1486.57628,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1486.57628,"mean_force":1486.57628,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50751,0.08805,0.02703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.49831,0.05966,0.00901],"force_p95":2.8438,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.89743,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4913,0.1865,0.26562]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49777,0.19644,0.29131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":206.0,"contact_point_centroid":[0.49412,0.05874,0.00938],"force_p95":0.56062,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5959,"mean_force":0.54555,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48976,0.18307,0.17774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.49397,0.05898,0.00939],"force_p95":0.55031,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54615,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48951,0.14781,0.0733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.49413,0.05954,0.00939],"force_p95":0.54912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5493,"mean_force":0.54593,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49775,0.09841,0.03864]}],"total_contact_groups":6},"final_pose_error":0.13391,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49412,0.05879,0.03391],"final_tcp_position":[0.50819,0.0873,0.02556],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":1486.57628,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":71.0,"n_steps_budget":630.0,"object_pos_end":[0.49411,0.05897,0.03358],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.47508,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":77.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.48673,0.17948,0.24811],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.49415,0.05905,0.03384],"object_pos_start":[0.49411,0.05897,0.03358],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.13924,"object_z_max":0.03384,"peak_contact_force":0.54825,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":206.0,"raw_peak_contact_force":0.5959,"subtask_id":"reach_contact","tcp_end":[0.49386,0.18776,0.10549],"tcp_start":[0.48673,0.17948,0.24811],"tcp_to_object_dist_end":0.14731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":599.0,"n_steps_budget":660.0,"object_pos_end":[0.49416,0.05879,0.03391],"object_pos_start":[0.49415,0.05905,0.03384],"object_to_goal_dist_end":0.13905,"object_to_goal_dist_start":0.13931,"object_z_max":0.03391,"peak_contact_force":0.54312,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":599.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_contact","tcp_end":[0.48822,0.10802,0.04526],"tcp_start":[0.49386,0.18776,0.10549],"tcp_to_object_dist_end":0.05086,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.49412,0.05879,0.03391],"object_pos_start":[0.49416,0.05879,0.03391],"object_to_goal_dist_end":0.13905,"object_to_goal_dist_start":0.13905,"object_z_max":0.03391,"peak_contact_force":107.81065,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":19.0,"raw_peak_contact_force":1486.57628,"subtask_id":"push_complete","tcp_end":[0.50819,0.0873,0.02556],"tcp_start":[0.48822,0.10802,0.04526],"tcp_to_object_dist_end":0.03287,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94444,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":3e-05,"approach_peg.approach_offset_y":0.07057,"approach_peg.approach_offset_z":0.08719,"approach_peg.pose_tolerance":0.02539,"contact_peg.approach_offset_x":0.01984,"contact_peg.contact_offset_y":0.01827,"contact_peg.contact_offset_z":0.0146,"contact_peg.force_threshold":13.01228,"descend_to_peg.approach_offset_x":0.0045,"descend_to_peg.approach_offset_y":0.05211,"descend_to_peg.descend_offset_z":0.03267,"descend_to_peg.pose_tolerance":0.02231,"push_phase.max_time":6.45003,"push_phase.push_distance":0.15869,"push_phase.push_speed":0.04846,"push_phase.retry_offset_x":-9e-05,"push_phase.retry_offset_y":-0.00063},"optimized_scores":{"best_composite_score":-0.58288,"best_fitness_score":0.10712,"best_task_score":2e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52503,0.11991,0.06],"force_p95":439.5097,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":439.5097,"mean_force":439.5097,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.52023,0.13118,0.05442]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.11997,0.06],"force_p95":53.35871,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.35871,"mean_force":53.35871,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52019,0.13128,0.05452]},{"body_a":"peg","body_b":"channel_base_body","contact_count":96.0,"contact_point_centroid":[0.50427,0.08099,0.00925],"force_p95":1.74783,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.70584,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51377,0.20002,0.25799]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50248,0.19989,0.29276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":205.0,"contact_point_centroid":[0.50605,0.08093,0.00938],"force_p95":0.55054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55543,"mean_force":0.5467,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51694,0.19668,0.16952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.50598,0.0808,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5138,0.16213,0.07944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49001,0.08914,0.00938],"force_p95":0.54527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54527,"mean_force":0.54527,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.52023,0.13118,0.05442]}],"total_contact_groups":7},"final_pose_error":0.15905,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.0809,0.03378],"final_tcp_position":[0.52031,0.13121,0.05426],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":439.5097,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":125.0,"n_steps_budget":630.0,"object_pos_end":[0.506,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55517,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":132.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.52375,0.20031,0.22941],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":205.0,"n_steps_budget":900.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.506,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54449,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":205.0,"raw_peak_contact_force":0.55543,"subtask_id":"reach_contact","tcp_end":[0.51051,0.19334,0.10856],"tcp_start":[0.52375,0.20031,0.22941],"tcp_to_object_dist_end":0.13514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":53.35871,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":514.0,"raw_peak_contact_force":53.35871,"subtask_id":"reach_contact","tcp_end":[0.52023,0.13118,0.05442],"tcp_start":[0.51051,0.19334,0.10856],"tcp_to_object_dist_end":0.05621,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":439.5097,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":439.5097,"subtask_id":"push_complete","tcp_end":[0.52031,0.13121,0.05426],"tcp_start":[0.52023,0.13118,0.05442],"tcp_to_object_dist_end":0.05618,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```