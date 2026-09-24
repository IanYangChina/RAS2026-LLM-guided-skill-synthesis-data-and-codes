## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.1152 | 0.03 | ❌ rejected |
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | -0.1495 | 0.10 | ❌ rejected |
| 5 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.1748 | 0.05 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | -0.1683 | 0.02 | ❌ rejected |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | -0.0113 | 0.10 | ✅ accepted |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.115) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.1
    - 0.1
    tolerance: 0.01
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.1
    - 0.04
    tolerance: 0.01
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_detect
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: contact
- id: push_through_channel
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
    tolerance: 0.02
  parameters:
    max_time:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: duration.max_time
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
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.1, 0.1], tolerance=0.01
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.1, 0.04], tolerance=0.01
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_detect, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.115
- **task_score** (E): 0.031
- **fitness_score**: 0.125  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_peg | 1.00 | 1.00 | 0.2145 |
| descend_to_push_height | 1.00 | 1.00 | 0.0623 |
| align_to_peg | 1.00 | 1.00 | 0.0084 |
| contact_peg | 1.00 | 1.00 | 0.0002 |
| push_through_channel | 0.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.111, 0.107) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.546 | 4.034 |
| descend_to_push_height | descend | 1.00 / step_budget | (0.508, 0.111, 0.107)→(0.501, 0.108, 0.048) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.667 | 221.327 | 329.743 |
| align_to_peg | align | 1.00 / step_budget | (0.501, 0.108, 0.048)→(0.499, 0.105, 0.041) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 180.672 | 314.149 |
| contact_peg | contact | 1.00 / force_exceeded | (0.499, 0.105, 0.041)→(0.499, 0.105, 0.041) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 58.967 | 58.967 |
| push_through_channel | push | 0.00 / guard_failure | (0.499, 0.105, 0.041)→(0.497, 0.084, 0.039) | (0.502, 0.067, 0.034)→(0.502, 0.049, 0.035) | 0.147→0.130 | 1.00 / 2.000 | 47.323 | 60.382 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.323
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.094
- phase_score: 0.208
- phase_breakdown.approach_score: 0.264
- phase_breakdown.contact_score: 0.470
- phase_breakdown.push_score: 0.103

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.163
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.094
- **Median Q (composite search score)**: -0.131
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82979,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.0304,"approach_behind_peg.approach_speed":0.05823,"contact_peg.contact_force_threshold":14.10293,"contact_peg.contact_speed":0.02143,"descend_to_push_height.descend_speed":0.03927,"push_through_channel.max_time":12.31059,"push_through_channel.push_speed":0.03145},"optimized_scores":{"best_composite_score":-0.13749,"best_fitness_score":0.10251,"best_task_score":5e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":79.0,"contact_point_centroid":[0.52511,0.10376,0.05995],"force_p95":344.91374,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":360.17147,"mean_force":330.05358,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.50658,0.1037,0.04746]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":443.0,"contact_point_centroid":[0.52503,0.10341,0.05999],"force_p95":305.87772,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.52866,"mean_force":248.84804,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.50448,0.10329,0.04425]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,0.10292,0.05998],"force_p95":76.0939,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.0939,"mean_force":76.0939,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50297,0.10275,0.04172]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,0.10292,0.05998],"force_p95":71.36303,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.36303,"mean_force":71.36303,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50298,0.10275,0.04173]},{"body_a":"peg","body_b":"channel_base_body","contact_count":720.0,"contact_point_centroid":[0.50584,0.063,0.00936],"force_p95":0.55907,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56535,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.51157,0.15247,0.19893]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49979,0.1984,0.29671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":444.0,"contact_point_centroid":[0.50602,0.06301,0.00938],"force_p95":0.55276,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54657,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.50448,0.10329,0.04425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.50581,0.06302,0.00938],"force_p95":0.55207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55419,"mean_force":0.5466,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.51287,0.10508,0.06931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51932,0.05092,0.00938],"force_p95":0.54684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54684,"mean_force":0.54684,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50297,0.10275,0.04172]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52372,0.06003,0.00938],"force_p95":0.54567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54567,"mean_force":0.54567,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50298,0.10275,0.04173]}],"total_contact_groups":10},"final_pose_error":0.18279,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.506,0.06292,0.03381],"final_tcp_position":[0.50295,0.10275,0.0417],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":360.17147,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54523,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":754.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.52433,0.108,0.10652],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06301,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":338.16272,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":346.0,"raw_peak_contact_force":360.17147,"tcp_end":[0.50595,0.10376,0.04688],"tcp_start":[0.52433,0.108,0.10652],"tcp_to_object_dist_end":0.0428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.50604,0.06297,0.03381],"object_pos_start":[0.50603,0.06301,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14327,"object_z_max":0.03381,"peak_contact_force":304.86561,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":887.0,"raw_peak_contact_force":323.52866,"tcp_end":[0.50298,0.10275,0.04173],"tcp_start":[0.50595,0.10376,0.04688],"tcp_to_object_dist_end":0.04068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.50603,0.06294,0.03381],"object_pos_start":[0.50604,0.06297,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":71.36303,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":71.36303,"subtask_id":"contact","tcp_end":[0.50297,0.10275,0.04172],"tcp_start":[0.50298,0.10275,0.04173],"tcp_to_object_dist_end":0.0407,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.06292,0.03381],"object_pos_start":[0.50603,0.06294,0.03381],"object_to_goal_dist_end":0.14318,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":76.0939,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":76.0939,"subtask_id":"push","tcp_end":[0.50295,0.10275,0.0417],"tcp_start":[0.50297,0.10275,0.04172],"tcp_to_object_dist_end":0.04072,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92818,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.03945,"approach_behind_peg.approach_speed":0.04809,"contact_peg.contact_force_threshold":14.13032,"contact_peg.contact_speed":0.02778,"descend_to_push_height.descend_speed":0.04923,"push_through_channel.max_time":10.80669,"push_through_channel.push_speed":0.04999},"optimized_scores":{"best_composite_score":-0.07742,"best_fitness_score":0.16258,"best_task_score":0.09414},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":477.0,"contact_point_centroid":[0.52506,0.09902,0.05997],"force_p95":342.66365,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":368.41007,"mean_force":283.34672,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.50781,0.09895,0.05137]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":268.0,"contact_point_centroid":[0.52508,0.09992,0.05997],"force_p95":331.0901,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.31442,"mean_force":319.60063,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.51155,0.09992,0.05881]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,0.09567,0.05998],"force_p95":39.11784,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.27575,"mean_force":17.65748,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50418,0.09551,0.04494]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":138.0,"contact_point_centroid":[0.54509,0.04318,0.06],"force_p95":32.75387,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.16277,"mean_force":24.16176,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49915,0.04516,0.03895]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52502,0.09553,0.05999],"force_p95":37.51501,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.61418,"mean_force":36.11367,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50396,0.09536,0.04462]},{"body_a":"attachment","body_b":"peg","contact_count":595.0,"contact_point_centroid":[0.50325,0.04874,0.04112],"force_p95":7.07955,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.10484,"mean_force":2.9974,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49933,0.0604,0.03913]},{"body_a":"peg","body_b":"channel_base_body","contact_count":609.0,"contact_point_centroid":[0.50585,0.02228,0.00985],"force_p95":7.28146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.25926,"mean_force":3.2463,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49969,0.06511,0.03955]},{"body_a":"peg","body_b":"channel_base_body","contact_count":745.0,"contact_point_centroid":[0.50594,0.05662,0.00936],"force_p95":0.60622,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56796,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.51491,0.14927,0.19853]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49987,0.19821,0.29639]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":173.0,"contact_point_centroid":[0.52501,0.02949,0.01312],"force_p95":2.21616,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.88177,"mean_force":0.90048,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49919,0.05587,0.03898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":409.0,"contact_point_centroid":[0.50614,0.05657,0.00938],"force_p95":0.5678,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62393,"mean_force":0.54663,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.51531,0.09999,0.06794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.50617,0.05667,0.00938],"force_p95":0.55016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5503,"mean_force":0.54674,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.50779,0.09894,0.05134]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49552,0.04998,0.00938],"force_p95":0.54933,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54975,"mean_force":0.54676,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50418,0.09551,0.04494]}],"total_contact_groups":13},"final_pose_error":0.11383,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50682,0.00492,0.03659],"final_tcp_position":[0.49922,0.03382,0.03902],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":368.41007,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05665,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.55128,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":782.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.53079,0.10199,0.10622],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":409.0,"n_steps_budget":990.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50613,0.05665,0.03377],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13693,"object_z_max":0.03378,"peak_contact_force":325.27763,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":677.0,"raw_peak_contact_force":340.31442,"tcp_end":[0.50995,0.10023,0.05572],"tcp_start":[0.53079,0.10199,0.10622],"tcp_to_object_dist_end":0.04897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":1.39159,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":961.0,"raw_peak_contact_force":368.41007,"tcp_end":[0.50425,0.09556,0.04506],"tcp_start":[0.50995,0.10023,0.05572],"tcp_to_object_dist_end":0.04062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":42.27575,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":42.27575,"subtask_id":"contact","tcp_end":[0.50403,0.0954,0.04471],"tcp_start":[0.50425,0.09556,0.04506],"tcp_to_object_dist_end":0.04033,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":756.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,0.00492,0.03659],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.08526,"object_to_goal_dist_start":0.13691,"object_z_max":0.03702,"peak_contact_force":0.98648,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1518.0,"raw_peak_contact_force":40.16277,"subtask_id":"push","tcp_end":[0.49922,0.03382,0.03902],"tcp_start":[0.50403,0.0954,0.04471],"tcp_to_object_dist_end":0.02999,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.03454,"approach_behind_peg.approach_speed":0.02979,"contact_peg.contact_force_threshold":14.08956,"contact_peg.contact_speed":0.04511,"descend_to_push_height.descend_speed":0.02779,"push_through_channel.max_time":15.16596,"push_through_channel.push_speed":0.03957},"optimized_scores":{"best_composite_score":-0.1308,"best_fitness_score":0.1092,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.47496,0.12,0.05991],"force_p95":280.0188,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.74202,"mean_force":227.69454,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.48301,0.12141,0.05591]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":351.0,"contact_point_centroid":[0.53263,0.11894,0.05996],"force_p95":241.07037,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.5071,"mean_force":183.9221,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.48758,0.11684,0.03706]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5345,0.11867,0.05997],"force_p95":64.88934,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.88934,"mean_force":64.88934,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48954,0.11662,0.03688]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53448,0.11867,0.05997],"force_p95":63.26293,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.26293,"mean_force":63.26293,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48953,0.11663,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":659.0,"contact_point_centroid":[0.49405,0.07997,0.00937],"force_p95":0.58414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56594,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.48333,0.16099,0.20036]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49902,0.19854,0.29663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":309.0,"contact_point_centroid":[0.49384,0.07983,0.00938],"force_p95":0.55108,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55472,"mean_force":0.54667,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.47696,0.12204,0.07341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.49385,0.07998,0.00938],"force_p95":0.55025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5504,"mean_force":0.54669,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.48746,0.11705,0.03727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49107,0.09768,0.00938],"force_p95":0.54869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54869,"mean_force":0.54869,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48953,0.11663,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47829,0.08906,0.00938],"force_p95":0.54144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54144,"mean_force":0.54144,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48954,0.11662,0.03688]}],"total_contact_groups":10},"final_pose_error":0.19693,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4938,0.07994,0.03378],"final_tcp_position":[0.48955,0.11662,0.03688],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":288.74202,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,0.07994,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54205,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":694.0,"raw_peak_contact_force":3.77147,"subtask_id":"approach","tcp_end":[0.46896,0.12436,0.10856],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07996,0.03378],"object_pos_start":[0.4938,0.07994,0.03378],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.54019,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":344.0,"raw_peak_contact_force":288.74202,"tcp_end":[0.48738,0.12037,0.04141],"tcp_start":[0.46896,0.12436,0.10856],"tcp_to_object_dist_end":0.04162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":391.0,"n_steps_budget":600.0,"object_pos_end":[0.49381,0.07997,0.03378],"object_pos_start":[0.49383,0.07996,0.03378],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":235.7577,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":742.0,"raw_peak_contact_force":250.5071,"tcp_end":[0.48953,0.11663,0.03688],"tcp_start":[0.48738,0.12037,0.04141],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49379,0.07996,0.03378],"object_pos_start":[0.49381,0.07997,0.03378],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16021,"object_z_max":0.03378,"peak_contact_force":63.26293,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":63.26293,"subtask_id":"contact","tcp_end":[0.48954,0.11662,0.03688],"tcp_start":[0.48953,0.11663,0.03688],"tcp_to_object_dist_end":0.03704,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,0.07994,0.03378],"object_pos_start":[0.49379,0.07996,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":64.88934,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":64.88934,"subtask_id":"push","tcp_end":[0.48955,0.11662,0.03688],"tcp_start":[0.48954,0.11662,0.03688],"tcp_to_object_dist_end":0.03706,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```