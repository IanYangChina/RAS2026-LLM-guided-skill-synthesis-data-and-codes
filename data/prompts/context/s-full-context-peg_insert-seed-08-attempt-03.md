## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3533 | 0.84 | ❌ rejected |
| 2 | approach → insert | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.4989 | 0.84 | ✅ accepted |
| 1 | approach → insert | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.4988 | 0.84 | ✅ accepted |
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

## Current Skill (Q=0.353) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_subtask
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: insert_subtask
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_socket
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
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_subtask
- id: insert_down
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
      distance: 0.055
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_limit:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 20.0
      binds_to:
      - path: guards.insert_force_limit.threshold
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
  - id: insert_force_limit
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
  subtask_id: insert_subtask

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.055], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **insert_down** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.055, mode=replace_offset_projection, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_limit: status=consumed; consumers=guards.insert_force_limit.threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=insert_force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0

## Design Metrics

- **Composite score**: 0.353
- **task_score** (E): 0.835
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_surface | 1.00 | 0.00 | 0.1427 |
| align_entry | 1.00 | 0.00 | 0.0536 |
| insert_down | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_surface | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, -0.001, 0.163) | (0.504, -0.000, 0.340)→(0.518, -0.001, 0.202) | 0.260→0.128 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_entry | descend | 1.00 / step_budget | (0.513, -0.001, 0.163)→(0.513, -0.001, 0.109) | (0.518, -0.001, 0.202)→(0.514, -0.001, 0.149) | 0.128→0.079 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_down | insert | 0.00 / guard_failure | (0.512, -0.001, 0.050)→(0.512, -0.001, 0.049) | (0.514, -0.001, 0.149)→(0.513, -0.000, 0.090) | 0.079→0.038 | 1.00 / 1.000 | 70.094 | 197.853 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.870
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.870
- phase_score: 0.566
- phase_breakdown.align_subtask_score: 0.533
- phase_breakdown.insert_subtask_score: 0.581
- phase_breakdown.approach_subtask_score: 0.552

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.870
- **Median Q (composite search score)**: 0.338
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.630


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93846,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.align_speed":0.09264,"approach_surface.approach_speed":0.06967,"insert_down.insertion_depth":0.04562,"insert_down.insertion_force_limit":33.89507,"insert_down.insertion_speed":0.02369},"optimized_scores":{"best_composite_score":0.31438,"best_fitness_score":0.59438,"best_task_score":0.80648},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.49686,0.03921,0.04974],"force_p95":192.59563,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":202.60696,"mean_force":124.19062,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.4819,0.03848,0.04985]}],"total_contact_groups":1},"final_pose_error":0.0157,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48199,0.03848,0.04952],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":202.60696,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.48835,0.03651,0.20333],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12915,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_surface","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.48377,0.03648,0.16359],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":181.0,"n_steps_budget":600.0,"object_pos_end":[0.48296,0.03819,0.1492],"object_pos_start":[0.48835,0.03651,0.20333],"object_to_goal_dist_end":0.08085,"object_to_goal_dist_start":0.12915,"object_z_max":0.20333,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align_subtask","tcp_end":[0.48239,0.03816,0.1092],"tcp_start":[0.48377,0.03648,0.16359],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.48288,0.03855,0.08979],"object_pos_start":[0.48296,0.03819,0.1492],"object_to_goal_dist_end":0.0433,"object_to_goal_dist_start":0.08085,"object_z_max":0.1492,"peak_contact_force":67.47128,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":202.60696,"subtask_id":"insert_subtask","tcp_end":[0.48199,0.03848,0.04952],"tcp_start":[0.48195,0.03848,0.04961],"tcp_to_object_dist_end":0.04029,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.42697,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.align_speed":0.02916,"approach_surface.approach_speed":0.0582,"insert_down.insertion_depth":0.07995,"insert_down.insertion_force_limit":31.43129,"insert_down.insertion_speed":0.00877},"optimized_scores":{"best_composite_score":0.40729,"best_fitness_score":0.68729,"best_task_score":0.86985},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53878,-0.0171,0.04973],"force_p95":179.58489,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.91889,"mean_force":121.06029,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.52379,-0.01688,0.04985]}],"total_contact_groups":1},"final_pose_error":0.0498,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52388,-0.01689,0.04951],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":187.91889,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.52949,-0.01623,0.20094],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12554,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_surface","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.52489,-0.01623,0.16121],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.52571,-0.01681,0.14889],"object_pos_start":[0.52949,-0.01623,0.20094],"object_to_goal_dist_end":0.07543,"object_to_goal_dist_start":0.12554,"object_z_max":0.20094,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align_subtask","tcp_end":[0.52511,-0.0168,0.1089],"tcp_start":[0.52489,-0.01623,0.16121],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.52483,-0.0169,0.08979],"object_pos_start":[0.52571,-0.01681,0.14889],"object_to_goal_dist_end":0.03159,"object_to_goal_dist_start":0.07543,"object_z_max":0.14889,"peak_contact_force":70.68315,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":187.91889,"subtask_id":"insert_subtask","tcp_end":[0.52388,-0.01689,0.04951],"tcp_start":[0.52383,-0.01689,0.04961],"tcp_to_object_dist_end":0.04029,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.5625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.align_speed":0.07375,"approach_surface.approach_speed":0.13119,"insert_down.insertion_depth":0.0792,"insert_down.insertion_force_limit":35.00607,"insert_down.insertion_speed":0.00947},"optimized_scores":{"best_composite_score":0.33831,"best_fitness_score":0.61831,"best_task_score":0.82868},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.54553,-0.0234,0.04969],"force_p95":193.42896,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.03403,"mean_force":127.38161,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.53054,-0.0231,0.04978]}],"total_contact_groups":1},"final_pose_error":0.04899,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.53064,-0.0231,0.04944],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":203.03403,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":671.0,"n_steps_budget":720.0,"object_pos_end":[0.53566,-0.02197,0.20254],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1295,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_surface","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.53105,-0.02196,0.16281],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":174.0,"n_steps_budget":600.0,"object_pos_end":[0.53244,-0.02298,0.14881],"object_pos_start":[0.53566,-0.02197,0.20254],"object_to_goal_dist_end":0.07947,"object_to_goal_dist_start":0.1295,"object_z_max":0.20254,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align_subtask","tcp_end":[0.53182,-0.02296,0.10882],"tcp_start":[0.53105,-0.02196,0.16281],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.53162,-0.02312,0.08972],"object_pos_start":[0.53244,-0.02298,0.14881],"object_to_goal_dist_end":0.04036,"object_to_goal_dist_start":0.07947,"object_z_max":0.14881,"peak_contact_force":72.12748,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":203.03403,"subtask_id":"insert_subtask","tcp_end":[0.53064,-0.0231,0.04944],"tcp_start":[0.53059,-0.0231,0.04954],"tcp_to_object_dist_end":0.04029,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```