## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1262 | 0.54 | ✅ accepted |
| 7 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ✅ accepted |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0777 | 0.03 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ❌ rejected |
| 4 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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

## Current Skill (Q=0.126) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_to_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.08
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.005
    orientation:
      mode: none
  subtask_id: contact
- id: push_through_channel
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
- id: retract_from_channel
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
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.08], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=none
  - parameter_bindings: none
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.126
- **task_score** (E): 0.542
- **fitness_score**: 0.336  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_peg | 1.00 | 1.00 | 0.1839 |
| descend_to_contact | 1.00 | 1.00 | 0.0927 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |
| retract_from_channel | 0.67 | 1.00 | 0.1682 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.141, 0.128) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.527 | 2.732 |
| descend_to_contact | descend | 1.00 / step_budget | (0.505, 0.141, 0.128)→(0.499, 0.120, 0.039) | (0.502, 0.098, 0.034)→(0.502, 0.086, 0.038) | 0.178→0.166 | 1.00 / 1.667 | 113.349 | 185.820 |
| push_through_channel | push | 0.00 / guard_failure | (0.498, 0.118, 0.038)→(0.498, 0.118, 0.038) | (0.502, 0.086, 0.038)→(0.502, 0.085, 0.037) | 0.166→0.165 | 1.00 / 2.000 | 106.136 | 121.363 |
| retract_from_channel | retract | 0.67 / step_budget | (0.498, 0.118, 0.038)→(0.495, -0.046, 0.076) | (0.502, 0.085, 0.037)→(0.502, -0.006, 0.028) | 0.165→0.076 | 1.00 / 1.667 | 1.085 | 123.754 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.960
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.960
- phase_score: 0.206
- phase_breakdown.approach_score: 0.170
- phase_breakdown.push_score: 0.016
- phase_breakdown.contact_score: 0.811

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.508
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.960
- **Median Q (composite search score)**: 0.125
- **K-run variance**: 0.0195
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.244


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2795,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.04392,"push_through_channel.force_threshold":27.78111,"push_through_channel.push_speed":0.01848},"optimized_scores":{"best_composite_score":0.29754,"best_fitness_score":0.50754,"best_task_score":0.96039},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5452,0.12,0.05994],"force_p95":233.86924,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.41879,"mean_force":156.92333,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49836,0.12772,0.0351]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.54283,0.11944,0.05998],"force_p95":76.74436,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.6883,"mean_force":58.41628,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49726,0.12177,0.03571]},{"body_a":"peg","body_b":"channel_base_body","contact_count":448.0,"contact_point_centroid":[0.50443,0.10834,0.00944],"force_p95":56.13,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.48383,"mean_force":5.40388,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5019,0.14347,0.08118]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.50702,0.1287,0.05743],"force_p95":74.04764,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.91776,"mean_force":54.68144,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50139,0.13847,0.05904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50494,0.09289,0.00998],"force_p95":17.34886,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.86478,"mean_force":2.63023,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49934,0.13179,0.03612]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50082,0.11734,0.03496],"force_p95":16.79415,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.02121,"mean_force":4.40773,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49852,0.12887,0.03528]},{"body_a":"attachment","body_b":"peg","contact_count":626.0,"contact_point_centroid":[0.49773,0.03212,0.05203],"force_p95":11.75873,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.1748,"mean_force":5.38012,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49517,0.04349,0.05264]},{"body_a":"peg","body_b":"channel_base_body","contact_count":870.0,"contact_point_centroid":[0.50535,0.00152,0.00956],"force_p95":10.32568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.68543,"mean_force":3.79972,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49547,0.03925,0.05412]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":300.0,"contact_point_centroid":[0.52503,-0.0129,0.03225],"force_p95":6.7165,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.45657,"mean_force":3.01847,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49517,0.03493,0.0548]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.50361,0.11163,0.00938],"force_p95":0.61306,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55791,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.50221,0.17651,0.2112]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49972,0.19943,0.29913]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.08348,0.06],"force_p95":0.23803,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24242,"mean_force":0.1985,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50081,0.13523,0.04593]}],"total_contact_groups":12},"final_pose_error":0.04447,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,-0.04189,0.0343],"final_tcp_position":[0.49584,-0.03864,0.07419],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":242.41879,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11177,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52678,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":585.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50603,0.15449,0.12848],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":449.0,"n_steps_budget":630.0,"object_pos_end":[0.50523,0.09069,0.04071],"object_pos_start":[0.50374,0.11177,0.03382],"object_to_goal_dist_end":0.17078,"object_to_goal_dist_start":0.19191,"object_z_max":0.04076,"peak_contact_force":0.48311,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":490.0,"raw_peak_contact_force":86.48383,"subtask_id":"contact","tcp_end":[0.50005,0.13282,0.03689],"tcp_start":[0.50603,0.15449,0.12848],"tcp_to_object_dist_end":0.04262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.50511,0.08646,0.0407],"object_pos_start":[0.50523,0.09069,0.04071],"object_to_goal_dist_end":0.16654,"object_to_goal_dist_start":0.17078,"object_z_max":0.04074,"peak_contact_force":242.41879,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":242.41879,"tcp_end":[0.49832,0.12732,0.03507],"tcp_start":[0.49835,0.12754,0.03508],"tcp_to_object_dist_end":0.0418,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,-0.04189,0.0343],"object_pos_start":[0.50512,0.08609,0.04062],"object_to_goal_dist_end":0.03916,"object_to_goal_dist_start":0.16617,"object_z_max":0.04062,"peak_contact_force":0.47613,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1841.0,"raw_peak_contact_force":220.6883,"tcp_end":[0.49584,-0.03864,0.07419],"tcp_start":[0.49832,0.12732,0.03507],"tcp_to_object_dist_end":0.04154,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29412,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.04231,"push_through_channel.force_threshold":39.95886,"push_through_channel.push_speed":0.0366},"optimized_scores":{"best_composite_score":0.12546,"best_fitness_score":0.33546,"best_task_score":0.51617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":60.0,"contact_point_centroid":[0.53823,0.12,0.05997],"force_p95":84.34602,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.0516,"mean_force":54.84847,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48972,0.132,0.03575]},{"body_a":"peg","body_b":"channel_base_body","contact_count":517.0,"contact_point_centroid":[0.49681,0.11498,0.0094],"force_p95":43.20539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.18715,"mean_force":4.82533,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48639,0.15043,0.08127]},{"body_a":"attachment","body_b":"peg","contact_count":88.0,"contact_point_centroid":[0.49537,0.13354,0.05294],"force_p95":69.99802,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.67251,"mean_force":25.33733,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48988,0.14396,0.0514]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54147,0.12,0.05991],"force_p95":70.93048,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.32986,"mean_force":48.91532,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49094,0.1397,0.03498]},{"body_a":"attachment","body_b":"peg","contact_count":398.0,"contact_point_centroid":[0.49683,0.07927,0.04327],"force_p95":19.11369,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.63409,"mean_force":9.4874,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48931,0.0878,0.04383]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":257.0,"contact_point_centroid":[0.52526,0.05406,0.03258],"force_p95":16.61055,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.15276,"mean_force":10.35296,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48949,0.07233,0.04719]},{"body_a":"peg","body_b":"channel_base_body","contact_count":924.0,"contact_point_centroid":[0.5007,0.04446,0.00898],"force_p95":13.63492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.71397,"mean_force":3.68402,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49076,0.05155,0.05259]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":36.0,"contact_point_centroid":[0.4749,0.06966,0.03656],"force_p95":8.9891,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.31954,"mean_force":1.54947,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49037,0.09133,0.04459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50744,0.09629,0.00977],"force_p95":2.84626,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.32803,"mean_force":1.30622,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49101,0.13976,0.03507]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49609,0.12809,0.04333],"force_p95":2.34395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.43407,"mean_force":1.5329,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49119,0.13989,0.03533]},{"body_a":"peg","body_b":"channel_base_body","contact_count":547.0,"contact_point_centroid":[0.49627,0.11911,0.00945],"force_p95":0.60509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55255,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49111,0.17984,0.21133]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49944,0.19924,0.29801]}],"total_contact_groups":12},"final_pose_error":0.05816,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49373,0.02506,0.0241],"final_tcp_position":[0.49387,-0.02523,0.07141],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":97.0516,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11924,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19937,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50922,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":571.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48413,0.16123,0.12934],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":533.0,"n_steps_budget":630.0,"object_pos_end":[0.49759,0.11051,0.03565],"object_pos_start":[0.49601,0.11924,0.03384],"object_to_goal_dist_end":0.19058,"object_to_goal_dist_start":0.19937,"object_z_max":0.03637,"peak_contact_force":0.17021,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":605.0,"raw_peak_contact_force":91.18715,"subtask_id":"contact","tcp_end":[0.49123,0.13991,0.03538],"tcp_start":[0.48413,0.16123,0.12934],"tcp_to_object_dist_end":0.03008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.49712,0.10995,0.03489],"object_pos_start":[0.49759,0.11051,0.03565],"object_to_goal_dist_end":0.19004,"object_to_goal_dist_start":0.19058,"object_z_max":0.03565,"peak_contact_force":74.32986,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":74.32986,"tcp_end":[0.49084,0.13961,0.03485],"tcp_start":[0.49088,0.13964,0.0349],"tcp_to_object_dist_end":0.03031,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49373,0.02506,0.0241],"object_pos_start":[0.497,0.10992,0.03479],"object_to_goal_dist_end":0.10644,"object_to_goal_dist_start":0.19001,"object_z_max":0.04067,"peak_contact_force":0.56201,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1675.0,"raw_peak_contact_force":97.0516,"tcp_end":[0.49387,-0.02523,0.07141],"tcp_start":[0.49084,0.13961,0.03485],"tcp_to_object_dist_end":0.06905,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32609,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.speed":0.05307,"push_through_channel.force_threshold":32.76893,"push_through_channel.push_speed":0.03793},"optimized_scores":{"best_composite_score":-0.04447,"best_fitness_score":0.16553,"best_task_score":0.14932},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":54.0,"contact_point_centroid":[0.52513,0.08712,0.05994],"force_p95":353.06273,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":379.79035,"mean_force":296.3784,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50522,0.08706,0.04454]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50524,0.05807,0.00945],"force_p95":12.68033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.87834,"mean_force":2.4507,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51281,0.09652,0.0801]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.50676,0.07656,0.04904],"force_p95":48.12158,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.46227,"mean_force":13.5448,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50612,0.08827,0.04916]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52506,0.0871,0.05997],"force_p95":46.95495,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.52255,"mean_force":15.81526,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50461,0.08701,0.0441]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52507,0.08711,0.05997],"force_p95":46.39927,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.33913,"mean_force":37.94061,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50469,0.08703,0.0442]},{"body_a":"peg","body_b":"channel_base_body","contact_count":952.0,"contact_point_centroid":[0.50043,0.00747,0.00854],"force_p95":8.95441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.55664,"mean_force":2.15634,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49864,0.00329,0.0625]},{"body_a":"attachment","body_b":"peg","contact_count":237.0,"contact_point_centroid":[0.50191,0.05267,0.04638],"force_p95":10.05744,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.3441,"mean_force":6.37024,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50103,0.06449,0.04669]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.0224,0.02423],"force_p95":7.35393,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.71887,"mean_force":4.06943,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49644,-0.07253,0.08308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49964,0.04248,0.00998],"force_p95":5.99011,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.03666,"mean_force":5.57115,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50469,0.08703,0.0442]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50469,0.07512,0.04426],"force_p95":5.69627,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.7443,"mean_force":5.26405,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50469,0.08703,0.0442]},{"body_a":"peg","body_b":"channel_base_body","contact_count":665.0,"contact_point_centroid":[0.50574,0.06297,0.00936],"force_p95":0.56013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56691,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.51161,0.15266,0.20887]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49981,0.1983,0.29675]}],"total_contact_groups":12},"final_pose_error":0.01012,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50499,-0.00079,0.02416],"final_tcp_position":[0.49642,-0.07331,0.0833],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":379.79035,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06304,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54461,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":699.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52434,0.10858,0.12634],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":420.0,"n_steps_budget":630.0,"object_pos_end":[0.50419,0.05778,0.03632],"object_pos_start":[0.50598,0.06304,0.03381],"object_to_goal_dist_end":0.13789,"object_to_goal_dist_start":0.1433,"object_z_max":0.0371,"peak_contact_force":339.39243,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":532.0,"raw_peak_contact_force":379.79035,"subtask_id":"contact","tcp_end":[0.50469,0.08703,0.04422],"tcp_start":[0.52434,0.10858,0.12634],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50416,0.05776,0.03632],"object_pos_start":[0.50419,0.05778,0.03632],"object_to_goal_dist_end":0.13787,"object_to_goal_dist_start":0.13789,"object_z_max":0.03632,"peak_contact_force":1.66072,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":47.33913,"tcp_end":[0.50468,0.08704,0.04416],"tcp_start":[0.50469,0.08703,0.04419],"tcp_to_object_dist_end":0.03031,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.50499,-0.00079,0.02416],"object_pos_start":[0.5041,0.05773,0.03634],"object_to_goal_dist_end":0.08093,"object_to_goal_dist_start":0.13784,"object_z_max":0.04057,"peak_contact_force":2.21674,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1195.0,"raw_peak_contact_force":53.52255,"tcp_end":[0.49642,-0.07331,0.0833],"tcp_start":[0.50468,0.08704,0.04416],"tcp_to_object_dist_end":0.09397,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```