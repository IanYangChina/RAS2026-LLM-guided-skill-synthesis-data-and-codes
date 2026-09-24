## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3881 | 0.84 | ✅ accepted |
| 8 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1689 | 0.84 | ✅ accepted |
| 7 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4131 | 0.84 | ❌ rejected |
| 6 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2189 | 0.84 | ✅ accepted |
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3587 | 0.64 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.48615778212844424, 0.03898214746703404, 0.08]
- Frozen socket pose: [0.48615778212844424, 0.03898214746703404, 0.025] (static fixture for this episode)
- Goal object position: (0.48615778212844424, 0.03898214746703404, 0.025)
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
  frozen_targets: {'socket_entry': [0.48615778212844424, 0.03898214746703404, 0.08]}
  frozen_fixtures: {'peg_socket': [0.48615778212844424, 0.03898214746703404, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.840, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.48615778212844424, 0.03898214746703404, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.48615778212844424, 0.03898214746703404, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.388) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: insertion_depth
  anchor: fixture
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_entry
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.055
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: reach_entry
- id: descend_contact
  type: descend
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: reach_entry
- id: insert_into_hole
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    guard_threshold:
      type: scalar
      range:
      - 30.0
      - 40.0
      default: 40.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth_distance:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_tolerance:
      type: scalar
      range:
      - 0.002
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.008
    - 0.008
    - 0.0
  subtask_id: insertion_depth

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_entry** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.055], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - guard_threshold: status=consumed; consumers=guards.force_guard.threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.008, 0.008, 0.0]

## Design Metrics

- **Composite score**: 0.388
- **task_score** (E): 0.840
- **fitness_score**: 0.435  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_entry | 1.00 | 0.1506 |
| descend_contact | 1.00 | 0.1035 |
| insert_into_hole | 0.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_entry | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, -0.000, 0.154) | (0.504, -0.000, 0.340)→(0.513, -0.000, 0.194) | 0.260→0.118 |
| descend_contact | descend | 1.00 / force_exceeded | (0.512, -0.000, 0.154)→(0.513, -0.001, 0.050) | (0.513, -0.000, 0.194)→(0.513, -0.001, 0.090) | 0.118→0.039 |
| insert_into_hole | insert | 0.00 / guard_failure | (0.513, -0.001, 0.050)→(0.513, -0.001, 0.050) | (0.513, -0.001, 0.090)→(0.513, -0.001, 0.090) | 0.039→0.039 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.872
- alignment_error: None
- terminal_score: 0.872
- phase_score: 0.165
- phase_breakdown.reach_entry_score: 0.547
- phase_breakdown.insertion_depth_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.448
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.872
- **Median Q (composite search score)**: 0.385
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.254


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6af64227b04102c511381eb024ec48290b429fbc7fcb6f0c4b42c66d0a974e9f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5cd76595591baa0f9f71873dced18f865534f529ba8f9daf4a3973579a78fb36`; realized-scene SHA-256: `586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45946,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_speed":0.14736,"descend_contact.contact_force_threshold":7.50474,"descend_contact.descend_speed":0.04895,"insert_into_hole.guard_threshold":37.75704,"insert_into_hole.insert_speed":0.02228,"insert_into_hole.insertion_depth_distance":0.04957,"insert_into_hole.insertion_tolerance":0.00697},"optimized_scores":{"best_composite_score":0.37848,"best_fitness_score":0.42515,"best_task_score":0.81606},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.49736,0.03929,0.04996],"force_p95":70.41258,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.3,"mean_force":51.98386,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.48241,0.03816,0.05009]}],"total_contact_groups":1},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48243,0.03816,0.05001],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"phases":[{"n_steps":276.0,"n_steps_budget":750.0,"object_pos_end":[0.48621,0.03323,0.19402],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11956,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.48576,0.03318,0.15402],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":621.0,"n_steps_budget":1000.0,"object_pos_end":[0.48284,0.03819,0.09014],"object_pos_start":[0.48621,0.03323,0.19402],"object_to_goal_dist_end":0.04308,"object_to_goal_dist_start":0.11956,"object_z_max":0.19402,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.48241,0.03816,0.05014],"tcp_start":[0.48576,0.03318,0.15402],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.48284,0.03819,0.09008],"object_pos_start":[0.48284,0.03819,0.09014],"object_to_goal_dist_end":0.04306,"object_to_goal_dist_start":0.04308,"object_z_max":0.09014,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_depth","tcp_end":[0.48243,0.03816,0.05001],"tcp_start":[0.48242,0.03816,0.05004],"tcp_to_object_dist_end":0.04007,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`; realized-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59016,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_speed":0.20375,"descend_contact.contact_force_threshold":6.50502,"descend_contact.descend_speed":0.05814,"insert_into_hole.guard_threshold":38.50923,"insert_into_hole.insert_speed":0.02136,"insert_into_hole.insertion_depth_distance":0.04322,"insert_into_hole.insertion_tolerance":0.00639},"optimized_scores":{"best_composite_score":0.40084,"best_fitness_score":0.4475,"best_task_score":0.87187},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53991,-0.01701,0.04996],"force_p95":59.20196,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.29934,"mean_force":50.64783,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.52493,-0.01678,0.0501]}],"total_contact_groups":1},"final_pose_error":0.01403,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52493,-0.01678,0.04999],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"phases":[{"n_steps":269.0,"n_steps_budget":600.0,"object_pos_end":[0.52334,-0.01457,0.19353],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11682,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.52285,-0.01456,0.15353],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.5254,-0.01678,0.09017],"object_pos_start":[0.52334,-0.01457,0.19353],"object_to_goal_dist_end":0.0321,"object_to_goal_dist_start":0.11682,"object_z_max":0.19353,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.52493,-0.01677,0.05017],"tcp_start":[0.52285,-0.01456,0.15353],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.5254,-0.01678,0.09008],"object_pos_start":[0.5254,-0.01678,0.09017],"object_to_goal_dist_end":0.03207,"object_to_goal_dist_start":0.0321,"object_z_max":0.09017,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_depth","tcp_end":[0.52493,-0.01678,0.04999],"tcp_start":[0.52493,-0.01678,0.05003],"tcp_to_object_dist_end":0.04009,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`; realized-scene SHA-256: `77fea26f11e91c54ae4a9c1f03cd5e6af1b4f6cac3191aa4cbd28ae81b548c93`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44444,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_speed":0.06459,"descend_contact.contact_force_threshold":6.87456,"descend_contact.descend_speed":0.06651,"insert_into_hole.guard_threshold":37.6907,"insert_into_hole.insert_speed":0.00606,"insert_into_hole.insertion_depth_distance":0.04683,"insert_into_hole.insertion_tolerance":0.00804},"optimized_scores":{"best_composite_score":0.38487,"best_fitness_score":0.43154,"best_task_score":0.8326},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.5466,-0.02358,0.04994],"force_p95":60.59953,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.69869,"mean_force":51.97256,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.53163,-0.02298,0.05006]}],"total_contact_groups":1},"final_pose_error":0.01748,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.53163,-0.02298,0.04996],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"phases":[{"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.52917,-0.02003,0.19304],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11845,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_entry","tcp_end":[0.52869,-0.02002,0.15304],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.53211,-0.02299,0.09013],"object_pos_start":[0.52917,-0.02003,0.19304],"object_to_goal_dist_end":0.04077,"object_to_goal_dist_start":0.11845,"object_z_max":0.19304,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_entry","tcp_end":[0.53162,-0.02297,0.05014],"tcp_start":[0.52869,-0.02002,0.15304],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53211,-0.02299,0.09005],"object_pos_start":[0.53211,-0.02299,0.09013],"object_to_goal_dist_end":0.04075,"object_to_goal_dist_start":0.04077,"object_z_max":0.09013,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_depth","tcp_end":[0.53163,-0.02298,0.04996],"tcp_start":[0.53163,-0.02298,0.05],"tcp_to_object_dist_end":0.04009,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```