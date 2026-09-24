## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | align → approach → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0382 | 0.87 | ❌ rejected |
| 7 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0426 | 0.87 | ❌ rejected |
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2064 | 0.99 | ❌ rejected |
| 5 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2064 | 0.99 | ❌ rejected |
| 4 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0357 | 0.88 | ❌ rejected |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5009457299760205, 0.03603709570607482, 0.08]
- Frozen socket pose: [0.5009457299760205, 0.03603709570607482, 0.025] (static fixture for this episode)
- Goal object position: (0.5009457299760205, 0.03603709570607482, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5009, 0.036, 0.08]
  frozen_socket_position: [0.5009, 0.036, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5009457299760205, 0.03603709570607482, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5009457299760205, 0.03603709570607482, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.038) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.09
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
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.07
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
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
    - 0.0
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.09], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.07]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.038
- **task_score** (E): 0.869
- **fitness_score**: 0.348  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1743 |
| approach_1 | 1.00 | 0.00 | 0.0304 |
| insert_1 | 0.00 | 1.00 | 0.0457 |
| retract_1 | 1.00 | 0.00 | 0.2286 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.481, -0.000, 0.129) | (0.504, -0.000, 0.340)→(0.486, -0.000, 0.169) | 0.260→0.094 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.481, -0.000, 0.129)→(0.479, -0.000, 0.099) | (0.486, -0.000, 0.169)→(0.484, -0.000, 0.139) | 0.094→0.067 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 0.00 / step_budget | (0.479, -0.000, 0.099)→(0.485, -0.000, 0.054) | (0.484, -0.000, 0.139)→(0.495, -0.000, 0.092) | 0.067→0.031 | 1.00 / 1.000 | 340.534 | 685.488 |
| retract_1 | retract | 1.00 / step_budget | (0.485, -0.000, 0.054)→(0.497, -0.000, 0.280) | (0.495, -0.000, 0.092)→(0.508, -0.000, 0.319) | 0.031→0.239 | 0.00 / 0.000 | 0.000 | 50.093 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.899
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.899
- phase_score: 0.001
- phase_breakdown.insert_score: 0.001
- phase_breakdown.approach_score: 0.001
- phase_breakdown.align_score: 0.001
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.360
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.899
- **Median Q (composite search score)**: 0.036
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.451


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `4865da8c78c0d766958c01aea638a491e86f6ad380c20093f3e1db2b764e8196`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `66fcf22dcc3bcf7c938cd95aa7e21cfd304510ff9d22bdf68d85d724037825f3`; realized-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50095,0.03604,0.025]},{"name":"target","value":[0.50095,0.03604,0.025]},{"name":"socket","value":[0.50095,0.03604,0.025]},{"name":"goal","value":[0.50095,0.03604,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.03604,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09016,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.05144,"approach_1.approach_speed":0.07999,"insert_1.insert_tolerance":0.0186,"insert_1.insertion_depth":0.14999,"retract_1.retract_speed":0.03732},"optimized_scores":{"best_composite_score":0.03639,"best_fitness_score":0.34639,"best_task_score":0.8646},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":448.0,"contact_point_centroid":[0.51328,0.0354,0.04988],"force_p95":383.75601,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":684.88754,"mean_force":358.30061,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49859,0.03468,0.05267]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.51616,0.03563,0.04997],"force_p95":53.77258,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.12756,"mean_force":51.95401,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50167,0.03466,0.05368]}],"total_contact_groups":2},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49806,0.00199,0.28028],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":684.88754,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.5021,0.03313,0.16845],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09448,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.49752,0.0331,0.12871],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.50164,0.03488,0.13853],"object_pos_start":[0.5021,0.03313,0.16845],"object_to_goal_dist_end":0.06815,"object_to_goal_dist_start":0.09448,"object_z_max":0.16845,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.49665,0.03482,0.09884],"tcp_start":[0.49752,0.0331,0.12871],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":518.0,"n_steps_budget":930.0,"object_pos_end":[0.51159,0.03534,0.09239],"object_pos_start":[0.50164,0.03488,0.13853],"object_to_goal_dist_end":0.0392,"object_to_goal_dist_start":0.06815,"object_z_max":0.13853,"peak_contact_force":330.84853,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":448.0,"raw_peak_contact_force":684.88754,"tcp_end":[0.5016,0.03467,0.05366],"tcp_start":[0.49665,0.03482,0.09884],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":763.0,"n_steps_budget":1000.0,"object_pos_end":[0.50851,0.00267,0.31889],"object_pos_start":[0.51159,0.03534,0.09239],"object_to_goal_dist_end":0.23905,"object_to_goal_dist_start":0.0392,"object_z_max":0.31859,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4.0,"raw_peak_contact_force":54.12756,"tcp_end":[0.49806,0.00199,0.28028],"tcp_start":[0.5016,0.03467,0.05366],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `93acd10de345eed07b6dc6c2bbc440a51ca07353b2db3e19ce9d53254358a6c5`; realized-scene SHA-256: `4c08395e36e43245f6092dd2e3719288cb8e1800970c3a851b5dc162486241ee`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42135,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.09788,"approach_1.approach_speed":0.01765,"insert_1.insert_tolerance":0.01975,"insert_1.insertion_depth":0.1495,"retract_1.retract_speed":0.08227},"optimized_scores":{"best_composite_score":0.05031,"best_fitness_score":0.36031,"best_task_score":0.89937},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":447.0,"contact_point_centroid":[0.49509,-0.01592,0.04988],"force_p95":401.07846,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":665.66873,"mean_force":372.72261,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48038,-0.0156,0.05259]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.49805,-0.01604,0.04996],"force_p95":49.15919,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.33652,"mean_force":47.67758,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48352,-0.0156,0.05363]}],"total_contact_groups":2},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.49688,-0.00096,0.28031],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":665.66873,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.48374,-0.01481,0.16935],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09202,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.47917,-0.01481,0.12961],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.48215,-0.01565,0.13871],"object_pos_start":[0.48374,-0.01481,0.16935],"object_to_goal_dist_end":0.06333,"object_to_goal_dist_start":0.09202,"object_z_max":0.16935,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.47718,-0.01564,0.09902],"tcp_start":[0.47917,-0.01481,0.12961],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":518.0,"n_steps_budget":930.0,"object_pos_end":[0.49338,-0.0159,0.09237],"object_pos_start":[0.48215,-0.01565,0.13871],"object_to_goal_dist_end":0.0212,"object_to_goal_dist_start":0.06333,"object_z_max":0.13871,"peak_contact_force":342.19694,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":447.0,"raw_peak_contact_force":665.66873,"tcp_end":[0.48347,-0.0156,0.05362],"tcp_start":[0.47718,-0.01564,0.09902],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":709.0,"n_steps_budget":1000.0,"object_pos_end":[0.50727,-0.00125,0.31894],"object_pos_start":[0.49338,-0.0159,0.09237],"object_to_goal_dist_end":0.23905,"object_to_goal_dist_start":0.0212,"object_z_max":0.31864,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":49.33652,"tcp_end":[0.49688,-0.00096,0.28031],"tcp_start":[0.48347,-0.0156,0.05362],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e4487702be29fc714aef807905297ccb2e376a648cd6f3407ac6d1ceee44c37e`; realized-scene SHA-256: `71c7bcc0411146bb1295ec697eba8abcb9eaa89bf878970856d0e0a8305cc755`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78808,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.07891,"approach_1.approach_speed":0.05006,"insert_1.insert_tolerance":0.0143,"insert_1.insertion_depth":0.14956,"retract_1.retract_speed":0.09928},"optimized_scores":{"best_composite_score":0.0279,"best_fitness_score":0.3379,"best_task_score":0.84338},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":425.0,"contact_point_centroid":[0.48104,-0.02078,0.04986],"force_p95":410.97948,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":705.90653,"mean_force":380.68163,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46635,-0.02034,0.05265]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.48381,-0.02092,0.04996],"force_p95":46.73274,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.81542,"mean_force":43.91089,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46931,-0.02032,0.05373]}],"total_contact_groups":2},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.49615,-0.00122,0.28055],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":705.90653,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.47085,-0.01934,0.16952],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09612,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.4663,-0.01933,0.12978],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":111.0,"n_steps_budget":600.0,"object_pos_end":[0.46857,-0.02044,0.13894],"object_pos_start":[0.47085,-0.01934,0.16952],"object_to_goal_dist_end":0.06985,"object_to_goal_dist_start":0.09612,"object_z_max":0.16952,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.46363,-0.02042,0.09924],"tcp_start":[0.4663,-0.01933,0.12978],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":497.0,"n_steps_budget":930.0,"object_pos_end":[0.47944,-0.02074,0.0924],"object_pos_start":[0.46857,-0.02044,0.13894],"object_to_goal_dist_end":0.03173,"object_to_goal_dist_start":0.06985,"object_z_max":0.13894,"peak_contact_force":348.5568,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":425.0,"raw_peak_contact_force":705.90653,"tcp_end":[0.46926,-0.02032,0.05372],"tcp_start":[0.46363,-0.02042,0.09924],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.50679,-0.00163,0.31911],"object_pos_start":[0.47944,-0.02074,0.0924],"object_to_goal_dist_end":0.23921,"object_to_goal_dist_start":0.03173,"object_z_max":0.31882,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":46.81542,"tcp_end":[0.49615,-0.00122,0.28055],"tcp_start":[0.46926,-0.02032,0.05372],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```