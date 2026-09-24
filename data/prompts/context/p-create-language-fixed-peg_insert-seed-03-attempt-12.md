## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0203 | 0.85 | ❌ rejected |
| 11 | approach → align → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1344 | 0.85 | ❌ rejected |
| 10 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1234 | 0.85 | ✅ accepted |
| 9 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.0261 | 0.85 | ❌ rejected |
| 8 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1199 | 0.85 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.46685193337148995, -0.021055159472312023, 0.08]
- Frozen socket pose: [0.46685193337148995, -0.021055159472312023, 0.025] (static fixture for this episode)
- Goal object position: (0.46685193337148995, -0.021055159472312023, 0.025)
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
  frozen_task_target: [0.4669, -0.0211, 0.08]
  frozen_socket_position: [0.4669, -0.0211, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.46685193337148995, -0.021055159472312023, 0.08]}
  frozen_fixtures: {'peg_socket': [0.46685193337148995, -0.021055159472312023, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e

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

## Current Skill (Q=-0.020) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: pre_align
  type: approach
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.18
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    pre_align_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align
- id: align_1
  type: approach
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lateral_tolerance
    when: during_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: align
- id: approach_1
  type: approach
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
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
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.07
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
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
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.05
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: insert

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **pre_align** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.18]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - pre_align_speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lateral_tolerance, when=during_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=repeat
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.07]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.05], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: -0.020
- **task_score** (E): 0.846
- **fitness_score**: 0.340  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pre_align | 1.00 | 0.00 | 0.0932 |
| approach_socket | 1.00 | 0.00 | 0.0987 |
| contact_detect | 0.00 | 0.00 | 0.0225 |
| insert_peg | 0.33 | 0.67 | 0.0064 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_align | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.001, 0.213) | (0.504, -0.000, 0.340)→(0.510, 0.001, 0.252) | 0.260→0.175 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_socket | approach | 1.00 / step_budget | (0.505, 0.001, 0.213)→(0.505, 0.001, 0.114) | (0.510, 0.001, 0.252)→(0.510, 0.001, 0.154) | 0.175→0.082 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_detect | contact | 0.00 / step_budget | (0.505, 0.001, 0.114)→(0.504, 0.001, 0.091) | (0.510, 0.001, 0.154)→(0.510, 0.001, 0.131) | 0.082→0.063 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_peg | insert | 0.33 / guard_failure | (0.503, 0.001, 0.064)→(0.503, 0.001, 0.058) | (0.510, 0.001, 0.131)→(0.504, 0.001, 0.098) | 0.063→0.039 | 0.67 / 0.667 | 60.982 | 95.183 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.872
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.872
- phase_score: 0.002
- phase_breakdown.approach_score: 0.002
- phase_breakdown.align_score: 0.006
- phase_breakdown.insert_score: 0.001
- phase_breakdown.contact_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.350
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.872
- **Median Q (composite search score)**: -0.013
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: insert_peg.insertion_depth
- **Final σ (mean)**: 0.348


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f11800d9c2e1994b03c35d775c68a936832c378ea82102a5404a99f161f65289`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ef8adc000d20c9595fb92eedb002c99ab6f0fb118834572ef2a426eae092b67`; realized-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98214,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_speed":0.07908,"contact_detect.contact_force":16.55491,"contact_detect.contact_speed":0.01394,"insert_peg.insert_speed":0.0269,"insert_peg.insertion_depth":0.01001,"pre_align.pre_align_speed":0.09015},"optimized_scores":{"best_composite_score":-0.03795,"best_fitness_score":0.32205,"best_task_score":0.80197},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46201,-0.02076,0.07352],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":285.0,"n_steps_budget":720.0,"object_pos_end":[0.47356,-0.01802,0.25384],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17676,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.469,-0.01801,0.2141],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":330.0,"n_steps_budget":870.0,"object_pos_end":[0.46889,-0.0206,0.15411],"object_pos_start":[0.47356,-0.01802,0.25384],"object_to_goal_dist_end":0.08297,"object_to_goal_dist_start":0.17676,"object_z_max":0.25384,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.46391,-0.02058,0.11442],"tcp_start":[0.469,-0.01801,0.2141],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.46805,-0.02087,0.13222],"object_pos_start":[0.46889,-0.0206,0.15411],"object_to_goal_dist_end":0.06468,"object_to_goal_dist_start":0.08297,"object_z_max":0.15411,"peak_contact_force":0.0,"phase_name":"contact_detect","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.46265,-0.02084,0.09259],"tcp_start":[0.46391,-0.02058,0.11442],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":70.0,"n_steps_budget":660.0,"object_pos_end":[0.46378,-0.02081,0.11348],"object_pos_start":[0.46805,-0.02087,0.13222],"object_to_goal_dist_end":0.05353,"object_to_goal_dist_start":0.06468,"object_z_max":0.13222,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert","tcp_end":[0.46201,-0.02076,0.07352],"tcp_start":[0.46265,-0.02084,0.09259],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3e77e957595308cac760f5f4d0307201511ded613ae0a20d2d9d48ef360ca4f0`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.42021,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_speed":0.06162,"contact_detect.contact_force":3.10725,"contact_detect.contact_speed":0.01412,"insert_peg.insert_speed":0.00682,"insert_peg.insertion_depth":0.06,"pre_align.pre_align_speed":0.05868},"optimized_scores":{"best_composite_score":-0.01023,"best_fitness_score":0.34977,"best_task_score":0.87167},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.544,0.00097,0.04988],"force_p95":140.57166,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.11137,"mean_force":117.71427,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.529,0.00079,0.05004]}],"total_contact_groups":1},"final_pose_error":0.03539,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52905,0.00079,0.04981],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":143.11137,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.53279,0.00076,0.25137],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17448,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.52819,0.00075,0.21164],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.53596,0.00083,0.15334],"object_pos_start":[0.53279,0.00076,0.25137],"object_to_goal_dist_end":0.08169,"object_to_goal_dist_start":0.17448,"object_z_max":0.25137,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.53086,0.00082,0.11367],"tcp_start":[0.52819,0.00075,0.21164],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.53609,0.00083,0.1303],"object_pos_start":[0.53596,0.00083,0.15334],"object_to_goal_dist_end":0.06192,"object_to_goal_dist_start":0.08169,"object_z_max":0.15334,"peak_contact_force":0.0,"phase_name":"contact_detect","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.53052,0.00081,0.09069],"tcp_start":[0.53086,0.00082,0.11367],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.52979,0.0008,0.08992],"object_pos_start":[0.53609,0.00083,0.1303],"object_to_goal_dist_end":0.0314,"object_to_goal_dist_start":0.06192,"object_z_max":0.1303,"peak_contact_force":92.31718,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":143.11137,"subtask_id":"insert","tcp_end":[0.52905,0.00079,0.04981],"tcp_start":[0.52902,0.00079,0.04993],"tcp_to_object_dist_end":0.04012,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f1677605f38c34d5c76967e3b08a88589314d198860b89f86514cd0f3e96f4b3`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.47368,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_speed":0.05232,"contact_detect.contact_force":17.04414,"contact_detect.contact_speed":0.01251,"insert_peg.insert_speed":0.00696,"insert_peg.insertion_depth":0.05921,"pre_align.pre_align_speed":0.08412},"optimized_scores":{"best_composite_score":-0.01268,"best_fitness_score":0.34732,"best_task_score":0.86553},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.53311,0.02493,0.04985],"force_p95":139.8472,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.43757,"mean_force":116.53391,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.51813,0.0242,0.04998]}],"total_contact_groups":1},"final_pose_error":0.03452,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51818,0.0242,0.04975],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":142.43757,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":315.0,"n_steps_budget":780.0,"object_pos_end":[0.52313,0.02134,0.25189],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17474,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.51856,0.02131,0.21215],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.52517,0.02404,0.15356],"object_pos_start":[0.52313,0.02134,0.25189],"object_to_goal_dist_end":0.08138,"object_to_goal_dist_start":0.17474,"object_z_max":0.25189,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.52011,0.024,0.11388],"tcp_start":[0.51856,0.02131,0.21215],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.52511,0.02432,0.1308],"object_pos_start":[0.52517,0.02404,0.15356],"object_to_goal_dist_end":0.06167,"object_to_goal_dist_start":0.08138,"object_z_max":0.15356,"peak_contact_force":0.0,"phase_name":"contact_detect","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.51958,0.02425,0.09119],"tcp_start":[0.52011,0.024,0.11388],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":153.0,"n_steps_budget":1000.0,"object_pos_end":[0.51888,0.02423,0.08986],"object_pos_start":[0.52511,0.02432,0.1308],"object_to_goal_dist_end":0.03226,"object_to_goal_dist_start":0.06167,"object_z_max":0.1308,"peak_contact_force":90.63026,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":142.43757,"subtask_id":"insert","tcp_end":[0.51818,0.0242,0.04975],"tcp_start":[0.51814,0.0242,0.04986],"tcp_to_object_dist_end":0.04011,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```