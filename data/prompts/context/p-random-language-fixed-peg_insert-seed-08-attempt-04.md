## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2781 | 0.84 | ✅ accepted |
| 3 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1057 | 0.84 | ✅ accepted |
| 2 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.0550 | 0.83 | ❌ rejected |
| 1 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1053 | 0.84 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.1274 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.48615778212844485, 0.03898214746703404, 0.08]
- Frozen socket pose: [0.48615778212844485, 0.03898214746703404, 0.025] (static fixture for this episode)
- Goal object position: (0.48615778212844485, 0.03898214746703404, 0.025)
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
  frozen_task_target: [0.4862, 0.039, 0.08]
  frozen_socket_position: [0.4862, 0.039, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.48615778212844485, 0.03898214746703404, 0.08]}
  frozen_fixtures: {'peg_socket': [0.48615778212844485, 0.03898214746703404, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480

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

## Current Skill (Q=0.278) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: align
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.1
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.09
  weight: 0.1
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.07
  weight: 0.1
- id: insert
  anchor: object
  metric: goal_progress
  offset:
  - 0.0
  - 0.0
  - 0.06
  weight: 0.7
phases:
- id: approach_to_socket
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
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
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach
- id: descend_to_entry
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.008
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: contact
- id: insert_into_hole
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    offset_along_axis:
      distance: 0.055
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.008
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.04
      - 0.08
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_threshold:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_high
    when: during_phase
    predicate: force_below
    threshold: 10.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insert

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08], tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}, tolerance=0.008
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_high, when=during_phase, predicate=force_below, on_failure=retry, threshold=10.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.278
- **task_score** (E): 0.837
- **fitness_score**: 0.336  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_socket | 1.00 | 0.00 | 0.1514 |
| descend_to_entry | 1.00 | 0.00 | 0.0419 |
| insert_into_hole | 0.67 | 0.67 | 0.0555 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_socket | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, -0.001, 0.153) | (0.504, -0.000, 0.340)→(0.513, -0.001, 0.193) | 0.260→0.119 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_entry | descend | 1.00 / step_budget | (0.513, -0.001, 0.153)→(0.513, -0.001, 0.111) | (0.513, -0.001, 0.193)→(0.514, -0.001, 0.151) | 0.119→0.081 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_hole | insert | 0.67 / force_exceeded | (0.513, -0.001, 0.111)→(0.512, -0.000, 0.056) | (0.514, -0.001, 0.151)→(0.513, -0.000, 0.096) | 0.081→0.041 | 0.67 / 0.667 | 46.094 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.873
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.873
- phase_score: 0.002
- phase_breakdown.insert_score: 0.001
- phase_breakdown.align_score: 0.000
- phase_breakdown.approach_score: 0.004
- phase_breakdown.contact_score: 0.003

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.350
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.873
- **Median Q (composite search score)**: 0.387
- **K-run variance**: 0.0275
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.363


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `111371231b67e0c9737e2a991f4190656c428bca2212422046741d75dd4bee83`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33ad86acc0270e6e89309305f52a6240db2b433d70da525d7c59722b30949f46`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52113,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_speed":0.23898,"descend_to_entry.descend_speed":0.23133,"insert_into_hole.insertion_depth":0.04001,"insert_into_hole.insertion_force_threshold":12.61542,"insert_into_hole.insertion_speed":0.03232},"optimized_scores":{"best_composite_score":0.04385,"best_fitness_score":0.32385,"best_task_score":0.80658},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00494,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48198,0.03851,0.06759],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":422.0,"n_steps_budget":600.0,"object_pos_end":[0.48486,0.03537,0.19408],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12039,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.48441,0.03533,0.15408],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":175.0,"n_steps_budget":600.0,"object_pos_end":[0.48334,0.03795,0.15195],"object_pos_start":[0.48486,0.03537,0.19408],"object_to_goal_dist_end":0.08303,"object_to_goal_dist_start":0.12039,"object_z_max":0.19408,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.48245,0.03788,0.11196],"tcp_start":[0.48441,0.03533,0.15408],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":283.0,"n_steps_budget":930.0,"object_pos_end":[0.48242,0.03854,0.10759],"object_pos_start":[0.48334,0.03795,0.15195],"object_to_goal_dist_end":0.05055,"object_to_goal_dist_start":0.08303,"object_z_max":0.15195,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert","tcp_end":[0.48198,0.03851,0.06759],"tcp_start":[0.48245,0.03788,0.11196],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7e8ba2d913c6be5a5528190a0c7ff1e14947b230e7e2c93846f050bf72228229`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.57895,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_speed":0.11396,"descend_to_entry.descend_speed":0.27396,"insert_into_hole.insertion_depth":0.07998,"insert_into_hole.insertion_force_threshold":27.88417,"insert_into_hole.insertion_speed":0.01546},"optimized_scores":{"best_composite_score":0.40353,"best_fitness_score":0.3502,"best_task_score":0.87267},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02577,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52393,-0.01687,0.05016],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":68.8626,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":478.0,"n_steps_budget":870.0,"object_pos_end":[0.52443,-0.01556,0.19308],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11674,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.52396,-0.01555,0.15309],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":170.0,"n_steps_budget":600.0,"object_pos_end":[0.52579,-0.01667,0.15128],"object_pos_start":[0.52443,-0.01556,0.19308],"object_to_goal_dist_end":0.07761,"object_to_goal_dist_start":0.11674,"object_z_max":0.19308,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.52485,-0.01665,0.11129],"tcp_start":[0.52396,-0.01555,0.15309],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.5244,-0.01687,0.09015],"object_pos_start":[0.52579,-0.01667,0.15128],"object_to_goal_dist_end":0.03136,"object_to_goal_dist_start":0.07761,"object_z_max":0.15128,"peak_contact_force":68.8626,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert","tcp_end":[0.52393,-0.01687,0.05016],"tcp_start":[0.52485,-0.01665,0.11129],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `6bfe353c76201464a4c9772ff30fffbe6279f45f6a3eb14a1a3a1447c56a946a`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.49143,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_speed":0.05015,"descend_to_entry.descend_speed":0.20449,"insert_into_hole.insertion_depth":0.07988,"insert_into_hole.insertion_force_threshold":24.6088,"insert_into_hole.insertion_speed":0.01031},"optimized_scores":{"best_composite_score":0.38703,"best_fitness_score":0.3337,"best_task_score":0.83149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02571,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.53067,-0.0231,0.05017],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":69.41976,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.53077,-0.02139,0.19254],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11862,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.53029,-0.02138,0.15254],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":168.0,"n_steps_budget":600.0,"object_pos_end":[0.5325,-0.02286,0.15108],"object_pos_start":[0.53077,-0.02139,0.19254],"object_to_goal_dist_end":0.08143,"object_to_goal_dist_start":0.11862,"object_z_max":0.19254,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.53156,-0.02283,0.11109],"tcp_start":[0.53029,-0.02138,0.15254],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.53115,-0.02311,0.09017],"object_pos_start":[0.5325,-0.02286,0.15108],"object_to_goal_dist_end":0.0401,"object_to_goal_dist_start":0.08143,"object_z_max":0.15108,"peak_contact_force":69.41976,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert","tcp_end":[0.53067,-0.0231,0.05017],"tcp_start":[0.53156,-0.02283,0.11109],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```