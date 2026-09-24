## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → align → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7  | 0.2213 | 0.05 | ❌ rejected |
| 10 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | 9  | 0.2352 | 0.00 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7  | 0.5858 | 0.17 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7  | 0.1914 | 0.24 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | -0.0379 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.038) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.02
  weight: 0.3
- id: push_through_channel
  target_entity: object
  metric: goal_progress
  weight: 0.4
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
    - 0.1
    orientation:
      mode: keep_current
      tolerance: 0.05
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
    approach_z:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above_peg
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.02
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    contact_force:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 12.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_low
    when: after_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: contact_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
      tolerance: 0.2
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.28
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_through_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1]
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z: status=consumed; consumers=target.offset.z (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.02]
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_low, when=after_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.038
- **task_score** (E): 0.155
- **fitness_score**: 0.372  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_retracted | 1.00 | 1.00 | 0.1496 |
| descend_to_peg | 0.00 | 1.00 | 0.1180 |
| align_and_contact | 1.00 | 1.00 | 0.0144 |
| push_through | 0.67 | 1.00 | 0.1719 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_retracted | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.491, 0.153, 0.162) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| descend_to_peg | descend | 0.00 / step_budget | (0.491, 0.153, 0.162)→(0.495, 0.110, 0.055) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.545 | 0.552 |
| align_and_contact | align | 1.00 / step_budget | (0.495, 0.110, 0.055)→(0.494, 0.096, 0.051) | (0.498, 0.068, 0.034)→(0.499, 0.067, 0.034) | 0.148→0.147 | 1.00 / 1.000 | 0.554 | 5.181 |
| push_through | push | 0.67 / step_budget | (0.494, 0.096, 0.051)→(0.494, -0.076, 0.049) | (0.499, 0.067, 0.034)→(0.495, 0.008, 0.024) | 0.147→0.089 | 1.00 / 1.000 | 0.631 | 32.230 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.376
- alignment_error: None
- force_efficiency: 0.535
- terminal_score: 0.259
- phase_score: 0.544
- phase_breakdown.push_through_channel_score: 0.402
- phase_breakdown.reach_above_peg_score: 0.816
- phase_breakdown.align_behind_peg_score: 0.600

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.430
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.259
- **Median Q (composite search score)**: -0.042
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.409


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23837,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.09908,"approach_retracted.approach_speed":0.26367,"approach_retracted.arc_height":0.14647,"descend_to_peg.contact_force":15.2877,"descend_to_peg.descend_speed":0.07154,"push_through.push_distance":0.169,"push_through.push_speed":0.02291},"optimized_scores":{"best_composite_score":0.01982,"best_fitness_score":0.42982,"best_task_score":0.25854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.4964,0.01506,0.00876],"force_p95":21.23041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.25348,"mean_force":5.26592,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48897,0.00611,0.04807]},{"body_a":"attachment","body_b":"peg","contact_count":362.0,"contact_point_centroid":[0.49383,0.04755,0.04705],"force_p95":22.08868,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.81146,"mean_force":13.01299,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48829,0.05757,0.04784]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.02829,0.02421],"force_p95":8.09892,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.9525,"mean_force":3.24538,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48989,-0.05018,0.04852]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.49475,0.0627,0.0094],"force_p95":0.73222,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.54166,"mean_force":0.67627,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48988,0.0994,0.05216]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49281,0.08154,0.05893],"force_p95":3.69954,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.89217,"mean_force":1.07799,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.49003,0.0933,0.05071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":437.0,"contact_point_centroid":[0.49561,0.06383,0.00936],"force_p95":0.59832,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56498,"phase_index":0.0,"phase_name":"approach_retracted","phase_type":"approach","tcp_position_centroid":[0.48716,0.19613,0.21706]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_retracted","phase_type":"approach","tcp_position_centroid":[0.49931,0.20104,0.29649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":727.0,"contact_point_centroid":[0.49509,0.06398,0.0094],"force_p95":0.55066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54539,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48359,0.12907,0.10457]}],"total_contact_groups":8},"final_pose_error":0.05177,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49342,0.00372,0.02413],"final_tcp_position":[0.49049,-0.07503,0.04889],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":23.25348,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.49516,0.06406,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55052,"phase_name":"approach_retracted","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":465.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_above_peg","tcp_end":[0.4788,0.15384,0.15993],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.49486,0.06403,0.03402],"object_pos_start":[0.49516,0.06406,0.03394],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.14427,"object_z_max":0.03402,"peak_contact_force":0.54239,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":727.0,"raw_peak_contact_force":0.55289,"subtask_id":"align_behind_peg","tcp_end":[0.49059,0.10582,0.05474],"tcp_start":[0.4788,0.15384,0.15993],"tcp_to_object_dist_end":0.04685,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.49547,0.06273,0.03437],"object_pos_start":[0.49486,0.06403,0.03402],"object_to_goal_dist_end":0.14291,"object_to_goal_dist_start":0.14424,"object_z_max":0.03423,"peak_contact_force":0.6128,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":90.0,"raw_peak_contact_force":4.54166,"subtask_id":"align_behind_peg","tcp_end":[0.49017,0.09199,0.05053],"tcp_start":[0.49059,0.10582,0.05474],"tcp_to_object_dist_end":0.03385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49342,0.00372,0.02413],"object_pos_start":[0.49547,0.06273,0.03437],"object_to_goal_dist_end":0.08546,"object_to_goal_dist_start":0.14291,"object_z_max":0.04037,"peak_contact_force":0.60162,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1364.0,"raw_peak_contact_force":23.25348,"subtask_id":"push_through_channel","tcp_end":[0.49049,-0.07503,0.04889],"tcp_start":[0.49017,0.09199,0.05053],"tcp_to_object_dist_end":0.0826,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09942,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.04264,"approach_retracted.approach_speed":0.22569,"approach_retracted.arc_height":0.14994,"descend_to_peg.contact_force":14.10819,"descend_to_peg.descend_speed":0.05761,"push_through.push_distance":0.14552,"push_through.push_speed":0.04081},"optimized_scores":{"best_composite_score":-0.04162,"best_fitness_score":0.36838,"best_task_score":0.12708},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.475,0.06984,0.04924],"force_p95":32.44628,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.27894,"mean_force":25.033,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48684,0.06984,0.04729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.4968,0.00965,0.00874],"force_p95":21.36754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.49277,"mean_force":5.31436,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48823,0.00116,0.0482]},{"body_a":"attachment","body_b":"peg","contact_count":367.0,"contact_point_centroid":[0.49313,0.04243,0.0469],"force_p95":22.19338,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.05785,"mean_force":12.97823,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48737,0.05228,0.04773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":78.0,"contact_point_centroid":[0.49462,0.05704,0.0094],"force_p95":0.7562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.82854,"mean_force":0.69557,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48864,0.09354,0.0514]},{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.49433,0.05895,0.00935],"force_p95":0.59091,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57808,"phase_index":0.0,"phase_name":"approach_retracted","phase_type":"approach","tcp_position_centroid":[0.47034,0.14826,0.24137]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49176,0.07654,0.05895],"force_p95":4.05212,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.20252,"mean_force":1.21644,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.48882,0.08822,0.0503]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_retracted","phase_type":"approach","tcp_position_centroid":[0.49706,0.19567,0.29781]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.49418,0.05903,0.00939],"force_p95":0.55047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54581,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47514,0.11593,0.10629]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.02242,0.0242],"force_p95":0.3715,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3715,"mean_force":0.3715,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48985,-0.07076,0.04927]}],"total_contact_groups":9},"final_pose_error":0.02925,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49382,-0.00203,0.02413],"final_tcp_position":[0.4901,-0.07961,0.04945],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":33.27894,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":488.0,"n_steps_budget":600.0,"object_pos_end":[0.49416,0.05885,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54257,"phase_name":"approach_retracted","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":494.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_above_peg","tcp_end":[0.46223,0.13459,0.1677],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.49385,0.05895,0.034],"object_pos_start":[0.49416,0.05885,0.03386],"object_to_goal_dist_end":0.13921,"object_to_goal_dist_start":0.13911,"object_z_max":0.034,"peak_contact_force":0.54661,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":968.0,"raw_peak_contact_force":0.55382,"subtask_id":"align_behind_peg","tcp_end":[0.48921,0.09944,0.05357],"tcp_start":[0.46223,0.13459,0.1677],"tcp_to_object_dist_end":0.04521,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":78.0,"n_steps_budget":600.0,"object_pos_end":[0.49465,0.0575,0.0347],"object_pos_start":[0.49385,0.05895,0.034],"object_to_goal_dist_end":0.1377,"object_to_goal_dist_start":0.13921,"object_z_max":0.03456,"peak_contact_force":0.5165,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":88.0,"raw_peak_contact_force":4.82854,"subtask_id":"align_behind_peg","tcp_end":[0.48902,0.08664,0.05014],"tcp_start":[0.48921,0.09944,0.05357],"tcp_to_object_dist_end":0.03346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,-0.00203,0.02413],"object_pos_start":[0.49465,0.0575,0.0347],"object_to_goal_dist_end":0.07981,"object_to_goal_dist_start":0.1377,"object_z_max":0.04037,"peak_contact_force":0.68445,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1381.0,"raw_peak_contact_force":33.27894,"subtask_id":"push_through_channel","tcp_end":[0.4901,-0.07961,0.04945],"tcp_start":[0.48902,0.08664,0.05014],"tcp_to_object_dist_end":0.08169,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80645,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.0441,"approach_retracted.approach_speed":0.2442,"approach_retracted.arc_height":0.13252,"descend_to_peg.contact_force":12.78425,"descend_to_peg.descend_speed":0.07946,"push_through.push_distance":0.15516,"push_through.push_speed":0.07702},"optimized_scores":{"best_composite_score":-0.09202,"best_fitness_score":0.31798,"best_task_score":0.07883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":332.0,"contact_point_centroid":[0.50424,0.06491,0.04802],"force_p95":35.26538,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.15657,"mean_force":21.07223,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50013,0.0758,0.0485]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.5046,0.03155,0.00868],"force_p95":29.94792,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.65353,"mean_force":7.07802,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50057,0.01695,0.04848]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":224.0,"contact_point_centroid":[0.52503,0.05402,0.0372],"force_p95":11.78592,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.65483,"mean_force":8.01778,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50002,0.07957,0.04844]},{"body_a":"peg","body_b":"channel_base_body","contact_count":77.0,"contact_point_centroid":[0.5062,0.07976,0.00938],"force_p95":0.59029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.17183,"mean_force":0.71644,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50271,0.11732,0.0537]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50445,0.0986,0.05887],"force_p95":5.49715,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.71482,"mean_force":3.40677,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50218,0.11051,0.05139]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.50569,0.0809,0.00935],"force_p95":0.56046,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57965,"phase_index":0.0,"phase_name":"approach_retracted","phase_type":"approach","tcp_position_centroid":[0.5168,0.20757,0.21953]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_retracted","phase_type":"approach","tcp_position_centroid":[0.50053,0.2022,0.29569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":501.0,"contact_point_centroid":[0.50591,0.08083,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51687,0.14741,0.10742]}],"total_contact_groups":8},"final_pose_error":0.02337,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49924,0.02087,0.02417],"final_tcp_position":[0.50176,-0.0726,0.04913],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":40.15657,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54612,"phase_name":"approach_retracted","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":500.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_above_peg","tcp_end":[0.53116,0.17045,0.15929],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":501.0,"n_steps_budget":960.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":501.0,"raw_peak_contact_force":0.55008,"subtask_id":"align_behind_peg","tcp_end":[0.50422,0.1239,0.05719],"tcp_start":[0.53116,0.17045,0.15929],"tcp_to_object_dist_end":0.049,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":77.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08015,0.03425],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16036,"object_to_goal_dist_start":0.16113,"object_z_max":0.03413,"peak_contact_force":0.53414,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":81.0,"raw_peak_contact_force":6.17183,"subtask_id":"align_behind_peg","tcp_end":[0.50218,0.10966,0.05118],"tcp_start":[0.50422,0.1239,0.05719],"tcp_to_object_dist_end":0.03423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49924,0.02087,0.02417],"object_pos_start":[0.50597,0.08015,0.03425],"object_to_goal_dist_end":0.1021,"object_to_goal_dist_start":0.16036,"object_z_max":0.04015,"peak_contact_force":0.60594,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1553.0,"raw_peak_contact_force":40.15657,"subtask_id":"push_through_channel","tcp_end":[0.50176,-0.0726,0.04913],"tcp_start":[0.50218,0.10966,0.05118],"tcp_to_object_dist_end":0.09678,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```