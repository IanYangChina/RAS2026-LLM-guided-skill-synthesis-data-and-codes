## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4315 | 0.09 | ❌ rejected |
| 5 | approach → approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4994 | 0.25 | ✅ accepted |
| 4 | approach → approach → descend → contact → push → retract | arc_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 19 | 0.0959 | 0.39 | ✅ accepted |
| 3 | align → approach → descend → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.0353 | 0.00 | ✅ accepted |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2873 | 0.24 | ✅ accepted |

**Proposal policy**: task_score is 0.09 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.431) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_1
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
    - 0.04
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
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
    - 0.005
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
    contact_offset_y:
      type: scalar
      range:
      - -0.005
      - 0.015
      default: 0.005
      binds_to:
      - path: target.offset.y
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_check
    when: after_phase
    predicate: force_below
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.002
    - 0.0
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
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
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Design Metrics

- **Composite score**: -0.431
- **task_score** (E): 0.087
- **fitness_score**: 0.155  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pre_approach_1 | 1.00 | 1.00 | 0.1617 |
| approach_1 | 1.00 | 1.00 | 0.0876 |
| descend_1 | 1.00 | 1.00 | 0.0412 |
| contact_1 | 1.00 | 1.00 | 0.0033 |
| push_1 | 0.00 | 1.00 | 0.0156 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.100, 0.177) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| approach_1 | approach | 1.00 / step_budget | (0.493, 0.100, 0.177)→(0.495, 0.106, 0.092) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.546 | 0.551 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.106, 0.092)→(0.494, 0.106, 0.051) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.544 | 8.485 |
| contact_1 | contact | 1.00 / force_exceeded | (0.492, 0.085, 0.035)→(0.492, 0.082, 0.033) | (0.498, 0.068, 0.034)→(0.502, 0.057, 0.035) | 0.148→0.138 | 1.00 / 2.333 | 1322.552 | 17.450 |
| push_1 | push | 0.00 / guard_failure | (0.492, 0.082, 0.033)→(0.501, 0.072, 0.026) | (0.503, 0.052, 0.035)→(0.504, 0.041, 0.036) | 0.132→0.121 | 1.00 / 3.000 | 574.813 | 1041.236 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.136
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.039
- phase_score: 0.215
- phase_breakdown.approach_score: 0.333
- phase_breakdown.push_score: 0.045
- phase_breakdown.contact_score: 0.608

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.189
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.157
- **Median Q (composite search score)**: -0.388
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62264,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.19354,"contact_1.contact_force_threshold":7.44887,"contact_1.contact_offset_y":0.00341,"contact_1.contact_speed":0.05216,"descend_1.descend_speed":0.04316,"descend_1.descend_z":0.01412,"pre_approach_1.pre_approach_arc_height":0.07026,"pre_approach_1.pre_approach_speed":0.1179,"push_1.push_depth":0.13634,"push_1.push_speed":0.02646,"retract_1.retract_height":0.12648,"retract_1.retract_speed":0.21248},"optimized_scores":{"best_composite_score":-0.53109,"best_fitness_score":0.18891,"best_task_score":0.15687},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50024,0.05197,0.05564],"force_p95":129.95798,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.95798,"mean_force":129.95798,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49047,0.06307,0.02778]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52509,0.03497,0.06],"force_p95":76.63297,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.63297,"mean_force":76.63297,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49047,0.06307,0.02778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50955,0.02078,0.00986],"force_p95":75.90997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.90997,"mean_force":75.90997,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49047,0.06307,0.02778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":564.0,"contact_point_centroid":[0.50332,0.03915,0.00984],"force_p95":6.07431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1936,"mean_force":3.18058,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48928,0.08117,0.03902]},{"body_a":"attachment","body_b":"peg","contact_count":429.0,"contact_point_centroid":[0.4956,0.06593,0.04918],"force_p95":5.84992,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.87401,"mean_force":3.62193,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48956,0.07728,0.03626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.49571,0.06385,0.00936],"force_p95":0.61426,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56797,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.48237,0.11753,0.25994]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.4983,0.19515,0.30041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.49506,0.06363,0.0094],"force_p95":0.55078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54551,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48817,0.10149,0.07399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.49444,0.06404,0.0094],"force_p95":0.55005,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55112,"mean_force":0.54576,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48188,0.09698,0.13467]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52504,0.03512,0.06],"force_p95":0.48012,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54386,"mean_force":0.22019,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49056,0.06336,0.02803]}],"total_contact_groups":10},"final_pose_error":0.16349,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50698,0.03657,0.03594],"final_tcp_position":[0.4906,0.06283,0.02761],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":129.95798,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":405.0,"n_steps_budget":900.0,"object_pos_end":[0.49512,0.06406,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54789,"phase_name":"pre_approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":406.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47688,0.09311,0.17632],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":171.0,"n_steps_budget":600.0,"object_pos_end":[0.49508,0.06366,0.03395],"object_pos_start":[0.49512,0.06406,0.03393],"object_to_goal_dist_end":0.14388,"object_to_goal_dist_start":0.14427,"object_z_max":0.03395,"peak_contact_force":0.54305,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":171.0,"raw_peak_contact_force":0.55112,"subtask_id":"approach","tcp_end":[0.48844,0.10111,0.09221],"tcp_start":[0.47688,0.09311,0.17632],"tcp_to_object_dist_end":0.06958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":130.0,"n_steps_budget":660.0,"object_pos_end":[0.49519,0.06366,0.03397],"object_pos_start":[0.49508,0.06366,0.03395],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14388,"object_z_max":0.03397,"peak_contact_force":0.5377,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":130.0,"raw_peak_contact_force":0.5516,"tcp_end":[0.48981,0.10225,0.05633],"tcp_start":[0.48844,0.10111,0.09221],"tcp_to_object_dist_end":0.04492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":607.0,"n_steps_budget":600.0,"object_pos_end":[0.50417,0.04228,0.03602],"object_pos_start":[0.49519,0.06366,0.03397],"object_to_goal_dist_end":0.12241,"object_to_goal_dist_start":0.14386,"object_z_max":0.03635,"peak_contact_force":12.35065,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":997.0,"raw_peak_contact_force":7.1936,"subtask_id":"contact","tcp_end":[0.49047,0.06307,0.02778],"tcp_start":[0.49074,0.06378,0.02845],"tcp_to_object_dist_end":0.02623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,0.03657,0.03594],"object_pos_start":[0.50691,0.0367,0.03596],"object_to_goal_dist_end":0.11685,"object_to_goal_dist_start":0.11698,"object_z_max":0.03596,"peak_contact_force":129.95798,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":129.95798,"subtask_id":"push","tcp_end":[0.4906,0.06283,0.02761],"tcp_start":[0.49047,0.06307,0.02778],"tcp_to_object_dist_end":0.03205,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54545,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10123,"contact_1.contact_force_threshold":3.16828,"contact_1.contact_offset_y":0.00558,"contact_1.contact_speed":0.04258,"descend_1.descend_speed":0.07057,"descend_1.descend_z":0.00383,"pre_approach_1.pre_approach_arc_height":0.04158,"pre_approach_1.pre_approach_speed":0.23171,"push_1.push_depth":0.07491,"push_1.push_speed":0.02972,"retract_1.retract_height":0.16681,"retract_1.retract_speed":0.14481},"optimized_scores":{"best_composite_score":-0.37495,"best_fitness_score":0.14505,"best_task_score":0.03948},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53528,0.0966,0.05945],"force_p95":1399.27006,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1399.27006,"mean_force":1399.27006,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50356,0.07462,0.02628]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.09389,0.04347],"force_p95":37.27991,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.4177,"mean_force":28.44823,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48683,0.0939,0.04151]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49506,0.0734,0.03768],"force_p95":33.49132,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.64388,"mean_force":17.7311,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49526,0.08501,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49824,0.04645,0.00942],"force_p95":29.19885,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.14257,"mean_force":8.87862,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49005,0.09037,0.03976]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.09801,0.05994],"force_p95":24.35392,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.35392,"mean_force":24.35392,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48684,0.09799,0.05808]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.09376,0.04337],"force_p95":7.71518,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7.71518,"mean_force":7.71518,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48682,0.09377,0.04141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":288.0,"contact_point_centroid":[0.49467,0.05885,0.00932],"force_p95":0.64116,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59697,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.47619,0.13103,0.24924]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.49695,0.19308,0.2977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":167.0,"contact_point_centroid":[0.49426,0.05855,0.00939],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54613,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48594,0.09803,0.06824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":185.0,"contact_point_centroid":[0.49381,0.05926,0.00939],"force_p95":0.55029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55186,"mean_force":0.5463,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47428,0.0984,0.13608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.4938,0.06085,0.00939],"force_p95":0.54983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55044,"mean_force":0.54607,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48741,0.09606,0.04329]}],"total_contact_groups":11},"final_pose_error":0.09087,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49653,0.03725,0.03815],"final_tcp_position":[0.5042,0.0738,0.02499],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":1399.27006,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":317.0,"n_steps_budget":600.0,"object_pos_end":[0.4942,0.05902,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54668,"phase_name":"pre_approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":323.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46497,0.09858,0.17957],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1538,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":185.0,"n_steps_budget":690.0,"object_pos_end":[0.49409,0.05884,0.03386],"object_pos_start":[0.4942,0.05902,0.03384],"object_to_goal_dist_end":0.1391,"object_to_goal_dist_start":0.13928,"object_z_max":0.03386,"peak_contact_force":0.54595,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":185.0,"raw_peak_contact_force":0.55186,"subtask_id":"approach","tcp_end":[0.48538,0.0984,0.09173],"tcp_start":[0.46497,0.09858,0.17957],"tcp_to_object_dist_end":0.07063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":167.0,"n_steps_budget":600.0,"object_pos_end":[0.49426,0.05894,0.03388],"object_pos_start":[0.49409,0.05884,0.03386],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.1391,"object_z_max":0.03388,"peak_contact_force":0.54863,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":168.0,"raw_peak_contact_force":24.35392,"tcp_end":[0.48857,0.09804,0.04573],"tcp_start":[0.48538,0.0984,0.09173],"tcp_to_object_dist_end":0.04125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":45.0,"n_steps_budget":600.0,"object_pos_end":[0.49398,0.05894,0.03389],"object_pos_start":[0.49426,0.05894,0.03388],"object_to_goal_dist_end":0.13921,"object_to_goal_dist_start":0.13919,"object_z_max":0.03389,"peak_contact_force":36.03986,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":48.0,"raw_peak_contact_force":37.4177,"subtask_id":"contact","tcp_end":[0.48682,0.09377,0.04141],"tcp_start":[0.48682,0.09382,0.04146],"tcp_to_object_dist_end":0.03634,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.49653,0.03725,0.03815],"object_pos_start":[0.49403,0.05885,0.03389],"object_to_goal_dist_end":0.11731,"object_to_goal_dist_start":0.13911,"object_z_max":0.03793,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":1399.27006,"subtask_id":"push","tcp_end":[0.5042,0.0738,0.02499],"tcp_start":[0.48682,0.09377,0.04141],"tcp_to_object_dist_end":0.0396,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34951,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14562,"contact_1.contact_force_threshold":7.59125,"contact_1.contact_offset_y":0.00707,"contact_1.contact_speed":0.05295,"descend_1.descend_speed":0.04865,"descend_1.descend_z":0.00867,"pre_approach_1.pre_approach_arc_height":0.0709,"pre_approach_1.pre_approach_speed":0.16747,"push_1.push_depth":0.10982,"push_1.push_speed":0.02373,"retract_1.retract_height":0.15144,"retract_1.retract_speed":0.17205},"optimized_scores":{"best_composite_score":-0.38842,"best_fitness_score":0.13158,"best_task_score":0.06339},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54382,0.08909,0.05974],"force_p95":1594.48042,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1594.48042,"mean_force":1594.48042,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50694,0.08049,0.02596]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52528,0.08242,0.05995],"force_p95":1203.41702,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1203.41702,"mean_force":1203.41702,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50694,0.08049,0.02596]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50407,0.07591,0.03718],"force_p95":26.88942,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.8424,"mean_force":12.96421,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50053,0.0876,0.02903]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52533,0.05643,0.03509],"force_p95":21.13287,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.19058,"mean_force":7.92905,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50208,0.08592,0.0283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.52066,0.04895,0.00971],"force_p95":19.19075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.07984,"mean_force":9.59642,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50333,0.08456,0.02771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.50702,0.05908,0.00983],"force_p95":6.38274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.73952,"mean_force":3.18191,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50035,0.10284,0.03797]},{"body_a":"attachment","body_b":"peg","contact_count":335.0,"contact_point_centroid":[0.50372,0.08749,0.04419],"force_p95":6.3596,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.38876,"mean_force":3.74251,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49992,0.09925,0.03535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":349.0,"contact_point_centroid":[0.50555,0.08094,0.00934],"force_p95":0.56722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59048,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.53085,0.12735,0.25897]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.50192,0.19387,0.30039]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":212.0,"contact_point_centroid":[0.52503,0.06891,0.02993],"force_p95":2.20234,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.28566,"mean_force":1.19079,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49975,0.09786,0.03446]},{"body_a":"peg","body_b":"channel_base_body","contact_count":158.0,"contact_point_centroid":[0.50608,0.0807,0.00938],"force_p95":0.55008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55014,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52454,0.11312,0.1348]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.50575,0.08086,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54675,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5066,0.11807,0.07234]}],"total_contact_groups":12},"final_pose_error":0.12847,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50734,0.04871,0.03458],"final_tcp_position":[0.50849,0.07884,0.0254],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":3920.41448,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":630.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54447,"phase_name":"pre_approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.53804,0.10916,0.17538],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.5482,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":158.0,"raw_peak_contact_force":0.55014,"subtask_id":"approach","tcp_end":[0.51077,0.11741,0.09282],"tcp_start":[0.53804,0.10916,0.17538],"tcp_to_object_dist_end":0.0696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":134.0,"n_steps_budget":660.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":134.0,"raw_peak_contact_force":0.55008,"tcp_end":[0.50384,0.11908,0.05201],"tcp_start":[0.51077,0.11741,0.09282],"tcp_to_object_dist_end":0.04237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":460.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,0.07108,0.03553],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.1513,"object_to_goal_dist_start":0.16113,"object_z_max":0.03574,"peak_contact_force":3919.26528,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":970.0,"raw_peak_contact_force":7.73952,"subtask_id":"contact","tcp_end":[0.49862,0.08967,0.02997],"tcp_start":[0.4999,0.09752,0.0339],"tcp_to_object_dist_end":0.02113,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.50734,0.04871,0.03458],"object_pos_start":[0.50699,0.06061,0.03571],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.14084,"object_z_max":0.03575,"peak_contact_force":1594.48042,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":1594.48042,"subtask_id":"push","tcp_end":[0.50849,0.07884,0.0254],"tcp_start":[0.49862,0.08967,0.02997],"tcp_to_object_dist_end":0.03152,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```