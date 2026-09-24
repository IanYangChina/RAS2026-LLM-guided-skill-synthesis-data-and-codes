## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0499 | 0.01 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0407 | 0.05 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0631 | 0.00 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2255 | 0.21 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2188 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=0.050) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.11
  weight: 0.2
- id: reach_behind
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.3
- id: reach_goal
  weight: 0.5
phases:
- id: approach_above
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
    - 0.11
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
  subtask_id: reach_above
- id: descend_to_push
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_behind
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: channel_left_wall
    offset:
    - -0.04
    - -0.097
    - 0.005
    orientation:
      mode: keep_current
  parameters:
    lateral_offset:
      type: scalar
      range:
      - -0.06
      - -0.02
      default: -0.04
      binds_to:
      - path: target.offset.x
        mode: replace
    push_depth:
      type: scalar
      range:
      - -0.12
      - -0.08
      default: -0.097
      binds_to:
      - path: target.offset.y
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.2
    - 0.3
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.11]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_push** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=fixture, entity=channel_left_wall, offset=[-0.04, -0.097, 0.005]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - push_depth: status=consumed; consumers=target.offset.y (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.050
- **task_score** (E): 0.009
- **fitness_score**: 0.210  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1822 |
| descend_to_contact | 1.00 | 1.00 | 0.0970 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| retract_1 | 0.00 | 1.00 | 0.1626 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.094, 0.155) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.530 | 4.034 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.508, 0.094, 0.155)→(0.500, 0.088, 0.060) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 24.271 | 24.271 |
| push_channel | push | 0.00 / guard_failure | (0.500, 0.081, 0.058)→(0.500, 0.081, 0.058) | (0.502, 0.067, 0.034)→(0.502, 0.063, 0.033) | 0.147→0.143 | 1.00 / 2.000 | 32.752 | 63.509 |
| retract_1 | retract | 0.00 / step_budget | (0.500, 0.081, 0.058)→(0.497, 0.154, 0.203) | (0.502, 0.063, 0.033)→(0.501, 0.062, 0.034) | 0.143→0.143 | 1.00 / 1.000 | 0.548 | 49.424 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.016
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.007
- phase_score: 0.356
- phase_breakdown.reach_above_score: 0.823
- phase_breakdown.contact_peg_score: 0.612
- phase_breakdown.reach_goal_score: 0.015

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.216
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.011
- **Median Q (composite search score)**: 0.051
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.487


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94388,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.08651,"descend_to_contact.contact_force_threshold":15.68196,"descend_to_contact.descend_speed":0.01,"push_channel.force_limit":59.99687,"push_channel.lateral_adjust":0.00315,"push_channel.push_depth":0.18232,"push_channel.push_speed":0.03346},"optimized_scores":{"best_composite_score":0.05052,"best_fitness_score":0.21052,"best_task_score":0.01132},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":54.0,"contact_point_centroid":[0.51409,0.05873,0.00924],"force_p95":58.07532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.98783,"mean_force":45.83176,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50654,0.08087,0.05867]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.5169,0.07505,0.05779],"force_p95":57.58197,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.4538,"mean_force":45.38562,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50654,0.08087,0.05867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50465,0.05872,0.00941],"force_p95":0.60761,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.77712,"mean_force":0.76149,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50142,0.11463,0.12894]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.51633,0.07298,0.05863],"force_p95":33.73452,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.19706,"mean_force":5.92555,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5055,0.07786,0.05979]},{"body_a":"peg","body_b":"channel_base_body","contact_count":507.0,"contact_point_centroid":[0.50593,0.0629,0.00938],"force_p95":0.55238,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.48372,"mean_force":0.58392,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51483,0.08697,0.10684]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51684,0.07736,0.05874],"force_p95":19.0233,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.0233,"mean_force":19.0233,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50709,0.0842,0.06017]},{"body_a":"peg","body_b":"channel_base_body","contact_count":598.0,"contact_point_centroid":[0.50576,0.06303,0.00936],"force_p95":0.56322,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56918,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51186,0.14275,0.22277]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49995,0.19773,0.29674]}],"total_contact_groups":8},"final_pose_error":0.10909,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50499,0.05811,0.03382],"final_tcp_position":[0.49977,0.15196,0.20205],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":60.98783,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54244,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":632.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_above","tcp_end":[0.52459,0.09011,0.15464],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.06304,0.03381],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":19.48372,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":508.0,"raw_peak_contact_force":19.48372,"subtask_id":"contact_peg","tcp_end":[0.50708,0.08419,0.06],"tcp_start":[0.52459,0.09011,0.15464],"tcp_to_object_dist_end":0.03368,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.50541,0.05868,0.03304],"object_pos_start":[0.50597,0.06304,0.03381],"object_to_goal_dist_end":0.13896,"object_to_goal_dist_start":0.1433,"object_z_max":0.03383,"peak_contact_force":47.89402,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":108.0,"raw_peak_contact_force":60.98783,"subtask_id":"reach_goal","tcp_end":[0.5065,0.07675,0.05786],"tcp_start":[0.5065,0.07683,0.05788],"tcp_to_object_dist_end":0.03072,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50499,0.05811,0.03382],"object_pos_start":[0.50541,0.05852,0.03301],"object_to_goal_dist_end":0.13834,"object_to_goal_dist_start":0.1388,"object_z_max":0.03569,"peak_contact_force":0.55071,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1037.0,"raw_peak_contact_force":49.77712,"tcp_end":[0.49977,0.15196,0.20205],"tcp_start":[0.5065,0.07675,0.05786],"tcp_to_object_dist_end":0.19271,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77027,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.05558,"descend_to_contact.contact_force_threshold":17.34639,"descend_to_contact.descend_speed":0.00709,"push_channel.force_limit":59.73032,"push_channel.lateral_adjust":0.00515,"push_channel.push_depth":0.17681,"push_channel.push_speed":0.03842},"optimized_scores":{"best_composite_score":0.04297,"best_fitness_score":0.20297,"best_task_score":0.0086},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.51467,0.05009,0.00923],"force_p95":59.35094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.95025,"mean_force":46.74596,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50822,0.07442,0.05852]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.51805,0.06772,0.05774],"force_p95":58.84896,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.4306,"mean_force":46.29797,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50822,0.07442,0.05852]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50477,0.05216,0.00941],"force_p95":0.62021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.29787,"mean_force":0.80333,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50263,0.10937,0.12751]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.51753,0.06551,0.0587],"force_p95":33.88763,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.7324,"mean_force":6.69694,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50719,0.07138,0.05977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50614,0.05669,0.00938],"force_p95":0.55645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.95041,"mean_force":0.60267,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51909,0.08071,0.10663]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51798,0.07024,0.05874],"force_p95":27.41735,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.41735,"mean_force":27.41735,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50887,0.07792,0.06012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":676.0,"contact_point_centroid":[0.50589,0.0566,0.00936],"force_p95":0.6006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57007,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51518,0.13954,0.22251]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49997,0.19768,0.2967]}],"total_contact_groups":8},"final_pose_error":0.11329,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50515,0.05148,0.03379],"final_tcp_position":[0.50049,0.148,0.19934],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":61.95025,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05664,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.55064,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":713.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_above","tcp_end":[0.53111,0.0838,0.15402],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,0.05663,0.0338],"object_pos_start":[0.50612,0.05664,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13692,"object_z_max":0.03379,"peak_contact_force":27.95041,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":490.0,"raw_peak_contact_force":27.95041,"subtask_id":"contact_peg","tcp_end":[0.50884,0.07791,0.05994],"tcp_start":[0.53111,0.0838,0.15402],"tcp_to_object_dist_end":0.03381,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.50565,0.05206,0.03307],"object_pos_start":[0.50617,0.05663,0.0338],"object_to_goal_dist_end":0.13237,"object_to_goal_dist_start":0.13691,"object_z_max":0.0338,"peak_contact_force":49.38033,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":114.0,"raw_peak_contact_force":61.95025,"subtask_id":"reach_goal","tcp_end":[0.50823,0.07012,0.05773],"tcp_start":[0.50823,0.07019,0.05775],"tcp_to_object_dist_end":0.03068,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50515,0.05148,0.03379],"object_pos_start":[0.50565,0.05191,0.03305],"object_to_goal_dist_end":0.13173,"object_to_goal_dist_start":0.13221,"object_z_max":0.03581,"peak_contact_force":0.54584,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1039.0,"raw_peak_contact_force":52.29787,"tcp_end":[0.50049,0.148,0.19934],"tcp_start":[0.50823,0.07012,0.05773],"tcp_to_object_dist_end":0.1917,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1068,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.03405,"descend_to_contact.contact_force_threshold":8.69318,"descend_to_contact.descend_speed":0.04358,"push_channel.force_limit":59.54567,"push_channel.lateral_adjust":0.00487,"push_channel.push_depth":0.19542,"push_channel.push_speed":0.00754},"optimized_scores":{"best_composite_score":0.05606,"best_fitness_score":0.21606,"best_task_score":0.0066},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.475,0.08836,0.05998],"force_p95":65.31378,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.58926,"mean_force":57.02238,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48381,0.09633,0.05869]},{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.49299,0.07988,0.00924],"force_p95":46.31446,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.11927,"mean_force":35.1682,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48381,0.09864,0.05926]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.4955,0.0967,0.05802],"force_p95":45.97041,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.79447,"mean_force":34.71601,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48381,0.09864,0.05926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49326,0.07744,0.00939],"force_p95":0.55291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.19746,"mean_force":0.6412,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48622,0.12899,0.1326]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.49535,0.09526,0.0582],"force_p95":21.17685,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.74828,"mean_force":5.34806,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48353,0.09629,0.05955]},{"body_a":"peg","body_b":"channel_base_body","contact_count":694.0,"contact_point_centroid":[0.49388,0.07995,0.00937],"force_p95":0.63367,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.3799,"mean_force":0.58239,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47577,0.10357,0.10624]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49555,0.09786,0.05875],"force_p95":24.8441,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.8441,"mean_force":24.8441,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48408,0.10094,0.06042]},{"body_a":"peg","body_b":"channel_base_body","contact_count":566.0,"contact_point_centroid":[0.49405,0.07992,0.00936],"force_p95":0.62963,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56894,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48362,0.15176,0.22448]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49894,0.19808,0.29689]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47494,0.07756,0.05852],"force_p95":1.07805,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70238,"mean_force":0.22972,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48345,0.0963,0.05963]}],"total_contact_groups":10},"final_pose_error":0.09991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49359,0.07731,0.03386],"final_tcp_position":[0.49159,0.16171,0.2081],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":67.58926,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,0.07994,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.49574,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":601.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_above","tcp_end":[0.46972,0.10682,0.15688],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.49386,0.07998,0.03379],"object_pos_start":[0.4938,0.07994,0.03377],"object_to_goal_dist_end":0.16022,"object_to_goal_dist_start":0.16018,"object_z_max":0.03379,"peak_contact_force":25.3799,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":695.0,"raw_peak_contact_force":25.3799,"subtask_id":"contact_peg","tcp_end":[0.48412,0.10095,0.0603],"tcp_start":[0.46972,0.10682,0.15688],"tcp_to_object_dist_end":0.03517,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.49347,0.07748,0.03324],"object_pos_start":[0.49386,0.07998,0.03379],"object_to_goal_dist_end":0.15776,"object_to_goal_dist_start":0.16022,"object_z_max":0.0338,"peak_contact_force":0.98204,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":89.0,"raw_peak_contact_force":67.58926,"subtask_id":"reach_goal","tcp_end":[0.48396,0.09596,0.05874],"tcp_start":[0.48393,0.09599,0.05873],"tcp_to_object_dist_end":0.0329,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49359,0.07731,0.03386],"object_pos_start":[0.4935,0.07742,0.03328],"object_to_goal_dist_end":0.15756,"object_to_goal_dist_start":0.1577,"object_z_max":0.03424,"peak_contact_force":0.54763,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1028.0,"raw_peak_contact_force":46.19746,"tcp_end":[0.49159,0.16171,0.2081],"tcp_start":[0.48396,0.09596,0.05874],"tcp_to_object_dist_end":0.19361,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```