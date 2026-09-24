## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | impedance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.0265 | 0.89 | ❌ rejected |
| 13 | approach → contact → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2230 | 0.80 | ❌ rejected |
| 12 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0482 | 0.86 | ❌ rejected |
| 11 | approach → contact → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.1718 | 0.76 | ❌ rejected |
| 10 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0118 | 0.89 | ❌ rejected |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.896, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.46685193337148995, -0.021055159472312023, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.46685193337148995, -0.021055159472312023, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.027) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insertion_complete
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - -0.05
  weight: 0.7
phases:
- id: approach_to_hover
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    hover_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_to_entry
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    descend_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: force_limit_descend
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: reach_pre_contact
- id: insert_into_hole
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
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_guard:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.insert_force_guard.threshold
        mode: replace
    insertion_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.02
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: insert_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: insertion_complete
- id: retract_from_hole
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
    - 0.15
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_hover** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - hover_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_entry** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=force_limit_descend, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_guard: status=consumed; consumers=guards.insert_force_guard.threshold (replace)
    - insertion_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=insert_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **retract_from_hole** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.027
- **task_score** (E): 0.886
- **fitness_score**: 0.437  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_hover | 0.00 | 1.00 | 0.1625 |
| descend_to_entry | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_hover | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.462, 0.004, 0.143) | (0.504, -0.000, 0.340)→(0.501, 0.004, 0.133) | 0.260→0.056 | 1.00 / 1.000 | 262.216 | 4333.172 |
| descend_to_entry | contact | 0.00 / guard_failure | (0.462, 0.004, 0.143)→(0.462, 0.004, 0.143) | (0.501, 0.004, 0.133)→(0.501, 0.004, 0.133) | 0.056→0.056 | 1.00 / 1.000 | 209.500 | 209.500 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.835
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.835
- phase_score: 0.240
- phase_breakdown.reach_pre_contact_score: 0.655
- phase_breakdown.insertion_complete_score: 0.063

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.478
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.925
- **Median Q (composite search score)**: 0.012
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.7619,"average_solve_count":21.0,"average_success_count":21.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_hover.approach_speed":0.11698,"approach_to_hover.hover_tolerance":0.02786,"descend_to_entry.descend_distance":0.11779,"descend_to_entry.descend_force_threshold":32.83061,"insert_into_hole.insertion_depth":0.03518,"insert_into_hole.insertion_force_guard":78.50251,"insert_into_hole.insertion_max_time":2.5696},"optimized_scores":{"best_composite_score":0.06829,"best_fitness_score":0.47829,"best_task_score":0.83506},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.49692,-0.00866,0.07966],"force_p95":10053.80565,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10682.62062,"mean_force":6528.0903,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.43143,-0.00857,0.08099]},{"body_a":"peg_socket","body_b":"link7","contact_count":305.0,"contact_point_centroid":[0.52623,-0.01528,0.06931],"force_p95":315.7704,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7010.61627,"mean_force":428.39502,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.44968,-0.00912,0.10562]},{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.43509,-0.01152,0.07963],"force_p95":3165.96852,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3556.42482,"mean_force":1316.52315,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.43282,-0.00857,0.08241]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5268,-0.01469,0.0658],"force_p95":183.32635,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":183.32635,"mean_force":183.32635,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"contact","tcp_position_centroid":[0.45476,-0.00921,0.11226]}],"total_contact_groups":4},"final_pose_error":0.11775,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.45479,-0.00921,0.11221],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":10682.62062,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.49388,-0.0101,0.10396],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02671,"object_to_goal_dist_start":0.26034,"object_z_max":0.34414,"peak_contact_force":297.39021,"phase_name":"approach_to_hover","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":336.0,"raw_peak_contact_force":10682.62062,"subtask_id":"reach_pre_contact","tcp_end":[0.45476,-0.00921,0.11226],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.49392,-0.01011,0.10393],"object_pos_start":[0.49388,-0.0101,0.10396],"object_to_goal_dist_end":0.02668,"object_to_goal_dist_start":0.02671,"object_z_max":0.10396,"peak_contact_force":183.32635,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":183.32635,"subtask_id":"insertion_complete","tcp_end":[0.45479,-0.00921,0.11221],"tcp_start":[0.45476,-0.00921,0.11226],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.90476,"average_solve_count":21.0,"average_success_count":21.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_hover.approach_speed":0.11588,"approach_to_hover.hover_tolerance":0.02813,"descend_to_entry.descend_distance":0.12964,"descend_to_entry.descend_force_threshold":37.00214,"insert_into_hole.insertion_depth":0.052,"insert_into_hole.insertion_force_guard":87.24656,"insert_into_hole.insertion_max_time":3.58697},"optimized_scores":{"best_composite_score":0.01232,"best_fitness_score":0.42232,"best_task_score":0.92484},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":17.0,"contact_point_centroid":[0.48512,0.00027,0.0776],"force_p95":1120.73651,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1160.54427,"mean_force":240.9055,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.48019,0.00027,0.08934]},{"body_a":"peg_socket","body_b":"link7","contact_count":178.0,"contact_point_centroid":[0.59039,0.00268,0.07956],"force_p95":392.09201,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":732.01341,"mean_force":261.31432,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.47432,0.00037,0.1351]},{"body_a":"peg_socket","body_b":"link6","contact_count":108.0,"contact_point_centroid":[0.59537,-0.00088,0.07976],"force_p95":302.12558,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":378.41161,"mean_force":241.95376,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.4697,0.00055,0.15048]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59541,-0.0009,0.07986],"force_p95":273.21856,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":273.21856,"mean_force":273.21856,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"contact","tcp_position_centroid":[0.47106,0.00064,0.15549]}],"total_contact_groups":4},"final_pose_error":0.12967,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.47098,0.00063,0.15552],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1160.54427,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":369.0,"n_steps_budget":600.0,"object_pos_end":[0.50992,0.00064,0.14602],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06677,"object_to_goal_dist_start":0.26034,"object_z_max":0.34569,"peak_contact_force":244.44524,"phase_name":"approach_to_hover","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":303.0,"raw_peak_contact_force":1160.54427,"subtask_id":"reach_pre_contact","tcp_end":[0.47106,0.00064,0.15549],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":810.0,"object_pos_end":[0.50984,0.00064,0.14604],"object_pos_start":[0.50992,0.00064,0.14602],"object_to_goal_dist_end":0.06677,"object_to_goal_dist_start":0.06677,"object_z_max":0.14602,"peak_contact_force":273.21856,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":273.21856,"subtask_id":"insertion_complete","tcp_end":[0.47098,0.00063,0.15552],"tcp_start":[0.47106,0.00064,0.15549],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.7619,"average_solve_count":21.0,"average_success_count":21.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_hover.approach_speed":0.1595,"approach_to_hover.hover_tolerance":0.02889,"descend_to_entry.descend_distance":0.12223,"descend_to_entry.descend_force_threshold":25.9551,"insert_into_hole.insertion_depth":0.03809,"insert_into_hole.insertion_force_guard":82.84459,"insert_into_hole.insertion_max_time":3.14122},"optimized_scores":{"best_composite_score":-0.00097,"best_fitness_score":0.40903,"best_task_score":0.89875},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.47903,0.01026,0.07742],"force_p95":1116.23225,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1156.35125,"mean_force":254.78406,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.47417,0.01023,0.089]},{"body_a":"peg_socket","body_b":"link7","contact_count":184.0,"contact_point_centroid":[0.58136,0.01826,0.07951],"force_p95":427.88601,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":741.09098,"mean_force":280.85286,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.46873,0.01474,0.14126]},{"body_a":"peg_socket","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.58434,0.0192,0.07978],"force_p95":281.05417,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":538.03176,"mean_force":253.12947,"phase_index":0.0,"phase_name":"approach_to_hover","phase_type":"approach","tcp_position_centroid":[0.46106,0.01927,0.15729]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58437,0.02037,0.07988],"force_p95":171.95395,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.95395,"mean_force":171.95395,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"contact","tcp_position_centroid":[0.46073,0.02078,0.16152]}],"total_contact_groups":4},"final_pose_error":0.12224,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.46072,0.02077,0.16153],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1156.35125,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.49915,0.02112,0.1504],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0735,"object_to_goal_dist_start":0.26034,"object_z_max":0.34543,"peak_contact_force":244.81239,"phase_name":"approach_to_hover","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":285.0,"raw_peak_contact_force":1156.35125,"subtask_id":"reach_pre_contact","tcp_end":[0.46073,0.02078,0.16152],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.49914,0.02111,0.15039],"object_pos_start":[0.49915,0.02112,0.1504],"object_to_goal_dist_end":0.07349,"object_to_goal_dist_start":0.0735,"object_z_max":0.1504,"peak_contact_force":171.95395,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":171.95395,"subtask_id":"insertion_complete","tcp_end":[0.46072,0.02077,0.16153],"tcp_start":[0.46073,0.02078,0.16152],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```