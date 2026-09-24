## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3368 | 0.88 | ✅ accepted |
| 10 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | time_limit | time_limit | pose_tolerance | 8 | 0.3567 | 0.88 | ❌ rejected |
| 9 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | time_limit | time_limit | pose_tolerance | 8 | 0.3563 | 0.88 | ❌ rejected |
| 8 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | time_limit | time_limit | pose_tolerance | 8 | 0.3567 | 0.88 | ✅ accepted |
| 7 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.5210 | 0.88 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5109569349857164, -0.018417062898890377, 0.08]
- Frozen socket pose: [0.5109569349857164, -0.018417062898890377, 0.025] (static fixture for this episode)
- Goal object position: (0.5109569349857164, -0.018417062898890377, 0.025)
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
  frozen_task_target: [0.511, -0.0184, 0.08]
  frozen_socket_position: [0.511, -0.0184, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5109569349857164, -0.018417062898890377, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5109569349857164, -0.018417062898890377, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.885, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.018417062898890377, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5109569349857164, -0.018417062898890377, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.337) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_socket
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: insert_peg
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_above
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
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
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: approach_socket
- id: insert_into_hole
  type: insert
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
      tolerance: 0.05
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    insert_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.008
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    insertion_distance:
      type: scalar
      range:
      - 0.03
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: retry.offset.y
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insert_peg
- id: retract_up
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
    - 0.14
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tolerance:
      type: scalar
      range:
      - 0.008
      - 0.02
      default: 0.012
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - insertion_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **retract_up** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.14]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.337
- **task_score** (E): 0.885
- **fitness_score**: 0.817  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.0921 |
| insert_into_hole | 1.00 | 0.00 | 0.1619 |
| retract_up | 1.00 | 0.00 | 0.1537 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.001, 0.211) | (0.504, -0.000, 0.340)→(0.496, -0.001, 0.251) | 0.260→0.173 | 1.00 / 1.000 | 416.028 | 469.961 |
| insert_into_hole | insert | 1.00 / step_budget | (0.496, -0.001, 0.211)→(0.498, 0.000, 0.050) | (0.496, -0.001, 0.251)→(0.498, 0.000, 0.090) | 0.173→0.027 | 0.00 / 0.000 | 0.000 | 61.882 |
| retract_up | retract | 1.00 / step_budget | (0.498, 0.000, 0.050)→(0.495, 0.000, 0.203) | (0.498, 0.000, 0.090)→(0.495, 0.000, 0.243) | 0.027→0.166 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.915
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.915
- phase_score: 0.815
- phase_breakdown.insert_peg_score: 0.871
- phase_breakdown.approach_socket_score: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.855
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.915
- **Median Q (composite search score)**: 0.348
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.312


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `193ea3a1ce1ed79056963f057d25ec25a24d300f4824e32f67c8dd96cb6cee27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a8b82e05e54fe244d72795229d8ab0587efc7638aafbc9b6be7ad9630911a897`; realized-scene SHA-256: `271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51096,-0.01842,0.025]},{"name":"target","value":[0.51096,-0.01842,0.025]},{"name":"socket","value":[0.51096,-0.01842,0.025]},{"name":"goal","value":[0.51096,-0.01842,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,-0.01842,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51096,-0.01842,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12418,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.31885,"approach_above.approach_tolerance":0.00754,"insert_into_hole.insert_speed":0.04953,"insert_into_hole.insert_tolerance":0.01291,"insert_into_hole.insertion_distance":0.04335,"insert_into_hole.retry_offset_x":0.01423,"insert_into_hole.retry_offset_y":0.00652,"retract_up.retract_speed":0.05577,"retract_up.retract_tolerance":0.01957},"optimized_scores":{"best_composite_score":0.37508,"best_fitness_score":0.85508,"best_task_score":0.91452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.52197,-0.01879,0.04963],"force_p95":370.83833,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":379.98908,"mean_force":280.88439,"phase_index":1.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.507,-0.01815,0.04942]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.52232,-0.01868,0.04953],"force_p95":75.90987,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.90265,"mean_force":41.86885,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50734,-0.01816,0.0492]}],"total_contact_groups":2},"final_pose_error":0.01951,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.50802,-0.01833,0.20071],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":379.98908,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":361.0,"n_steps_budget":600.0,"object_pos_end":[0.50748,-0.01638,0.24592],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16689,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":379.98908,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5.0,"raw_peak_contact_force":379.98908,"subtask_id":"approach_socket","tcp_end":[0.50703,-0.01637,0.20592],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.50763,-0.01816,0.08887],"object_pos_start":[0.50748,-0.01638,0.24592],"object_to_goal_dist_end":0.02161,"object_to_goal_dist_start":0.16689,"object_z_max":0.24592,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":10.0,"raw_peak_contact_force":83.90265,"subtask_id":"insert_peg","tcp_end":[0.50722,-0.01815,0.04887],"tcp_start":[0.50703,-0.01637,0.20592],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.50847,-0.01834,0.24071],"object_pos_start":[0.50763,-0.01816,0.08887],"object_to_goal_dist_end":0.16198,"object_to_goal_dist_start":0.02161,"object_z_max":0.24043,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50802,-0.01833,0.20071],"tcp_start":[0.50722,-0.01815,0.04887],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`; realized-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50095,0.03604,0.025]},{"name":"target","value":[0.50095,0.03604,0.025]},{"name":"socket","value":[0.50095,0.03604,0.025]},{"name":"goal","value":[0.50095,0.03604,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.03604,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08911,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.18299,"approach_above.approach_tolerance":0.01944,"insert_into_hole.insert_speed":0.05572,"insert_into_hole.insert_tolerance":0.01292,"insert_into_hole.insertion_distance":0.05025,"insert_into_hole.retry_offset_x":0.00472,"insert_into_hole.retry_offset_y":0.00989,"retract_up.retract_speed":0.03044,"retract_up.retract_tolerance":0.01536},"optimized_scores":{"best_composite_score":0.28718,"best_fitness_score":0.76718,"best_task_score":0.84788},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":89.0,"contact_point_centroid":[0.51367,0.0374,0.04977],"force_p95":514.81205,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":528.26496,"mean_force":448.94647,"phase_index":1.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.49892,0.03485,0.04967]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.51474,0.03868,0.04998],"force_p95":52.5619,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.75711,"mean_force":45.50101,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50023,0.03487,0.05011]}],"total_contact_groups":2},"final_pose_error":0.01526,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49819,0.03576,0.205],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":528.26496,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":172.0,"n_steps_budget":600.0,"object_pos_end":[0.49931,0.02801,0.25721],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17941,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":444.50411,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":89.0,"raw_peak_contact_force":528.26496,"subtask_id":"approach_socket","tcp_end":[0.49876,0.02797,0.21721],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.50058,0.03499,0.09009],"object_pos_start":[0.49931,0.02801,0.25721],"object_to_goal_dist_end":0.03642,"object_to_goal_dist_start":0.17941,"object_z_max":0.25721,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":52.75711,"subtask_id":"insert_peg","tcp_end":[0.50015,0.03488,0.05009],"tcp_start":[0.49876,0.02797,0.21721],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.49863,0.03579,0.24499],"object_pos_start":[0.50058,0.03499,0.09009],"object_to_goal_dist_end":0.16883,"object_to_goal_dist_start":0.03642,"object_z_max":0.24479,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49819,0.03576,0.205],"tcp_start":[0.50015,0.03488,0.05009],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`; realized-scene SHA-256: `4c08395e36e43245f6092dd2e3719288cb8e1800970c3a851b5dc162486241ee`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06867,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.46131,"approach_above.approach_tolerance":0.01178,"insert_into_hole.insert_speed":0.01451,"insert_into_hole.insert_tolerance":0.00908,"insert_into_hole.insertion_distance":0.05914,"insert_into_hole.retry_offset_x":0.00953,"insert_into_hole.retry_offset_y":0.00522,"retract_up.retract_speed":0.03701,"retract_up.retract_tolerance":0.01615},"optimized_scores":{"best_composite_score":0.3482,"best_fitness_score":0.8282,"best_task_score":0.89163},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":379.0,"contact_point_centroid":[0.47948,-0.02549,0.04992],"force_p95":476.80143,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":501.62828,"mean_force":440.69523,"phase_index":1.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.48239,-0.01573,0.04987]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.47374,-0.02392,0.04996],"force_p95":48.73484,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.98706,"mean_force":44.19733,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4864,-0.01588,0.04995]}],"total_contact_groups":2},"final_pose_error":0.01598,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47867,-0.01604,0.20418],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":501.62828,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":600.0,"object_pos_end":[0.48199,-0.01353,0.25128],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17276,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":423.59101,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":379.0,"raw_peak_contact_force":501.62828,"subtask_id":"approach_socket","tcp_end":[0.48154,-0.01352,0.21129],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48631,-0.01594,0.08993],"object_pos_start":[0.48199,-0.01353,0.25128],"object_to_goal_dist_end":0.02324,"object_to_goal_dist_start":0.17276,"object_z_max":0.25128,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":48.98706,"subtask_id":"insert_peg","tcp_end":[0.48639,-0.01589,0.04993],"tcp_start":[0.48154,-0.01352,0.21129],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.47909,-0.01604,0.24417],"object_pos_start":[0.48631,-0.01594,0.08993],"object_to_goal_dist_end":0.16628,"object_to_goal_dist_start":0.02324,"object_z_max":0.24395,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47867,-0.01604,0.20418],"tcp_start":[0.48639,-0.01589,0.04993],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```