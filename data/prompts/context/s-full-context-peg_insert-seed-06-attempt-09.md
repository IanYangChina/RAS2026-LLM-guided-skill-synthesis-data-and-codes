## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.2532 | 0.93 | ❌ rejected |
| 8 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1672 | 0.93 | ✅ accepted |
| 7 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.6663 | 0.88 | ❌ rejected |
| 6 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.1605 | 0.91 | ✅ accepted |
| 5 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.4902 | 0.87 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.93). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5030531481177548, -0.012538330414932925, 0.08]
- Frozen socket pose: [0.5030531481177548, -0.012538330414932925, 0.025] (static fixture for this episode)
- Goal object position: (0.5030531481177548, -0.012538330414932925, 0.025)
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
  frozen_task_target: [0.5031, -0.0125, 0.08]
  frozen_socket_position: [0.5031, -0.0125, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5030531481177548, -0.012538330414932925, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5030531481177548, -0.012538330414932925, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.930, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5030531481177548, -0.012538330414932925, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5030531481177548, -0.012538330414932925, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.253) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_socket
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: insert_peg
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.7
phases:
- id: approach_above
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.15
    offset_along_axis:
      distance: 0.0
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_height_offset:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_socket
- id: align_to_entry
  type: align
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
    - 0.05
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    align_height_offset:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    align_speed:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: approach_socket
- id: descend_to_contact
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
    - 0.025
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 12.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insert_peg
- id: insert_into_hole
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.06
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    insertion_distance:
      type: scalar
      range:
      - 0.04
      - 0.08
      default: 0.06
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    max_insertion_force:
      type: scalar
      range:
      - 15.0
      - 40.0
      default: 30.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=world_z, distance=0.0, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_height_offset: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **align_to_entry** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.05], tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - align_height_offset: status=consumed; consumers=target.offset.z (replace)
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - lateral_y: status=consumed; consumers=target.offset.y (add)
- **descend_to_contact** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.025], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_into_hole** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.06, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
    - max_insertion_force: status=consumed; consumers=guards.force_guard.threshold (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.01, 0.01, 0.0]

## Design Metrics

- **Composite score**: 0.253
- **task_score** (E): 0.929
- **fitness_score**: 0.780  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 0.00 | 0.0979 |
| align_to_entry | 1.00 | 0.00 | 0.1088 |
| descend_to_contact | 0.33 | 0.33 | 0.0579 |
| insert_into_hole | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.033, 0.211) | (0.504, -0.000, 0.340)→(0.498, 0.033, 0.251) | 0.260→0.176 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_entry | align | 1.00 / step_budget | (0.497, 0.033, 0.211)→(0.503, 0.013, 0.106) | (0.498, 0.033, 0.251)→(0.504, 0.013, 0.146) | 0.176→0.068 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_contact | contact | 0.33 / step_budget | (0.503, 0.013, 0.106)→(0.497, 0.018, 0.052) | (0.504, 0.013, 0.146)→(0.498, 0.018, 0.092) | 0.068→0.030 | 0.33 / 0.333 | 11.083 | 0.000 |
| insert_into_hole | push | 0.00 / guard_failure | (0.496, 0.018, 0.050)→(0.496, 0.018, 0.050) | (0.498, 0.018, 0.092)→(0.497, 0.018, 0.090) | 0.030→0.029 | 1.00 / 1.000 | 33.783 | 144.353 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.917
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.917
- phase_score: 0.677
- phase_breakdown.approach_socket_score: 0.228
- phase_breakdown.insert_peg_score: 0.869

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.803
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.989
- **Median Q (composite search score)**: 0.193
- **K-run variance**: 0.0130
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.323


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `60385b1f31aca3065ea31945cfeaa028cd4432c7d54684f37d7ce3abfb247b97`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4bee8669cc79b9d5e3314636941bfd5dcacadb9648a0bfff5f763dbb49e79a76`; realized-scene SHA-256: `8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98347,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_height_offset":0.06827,"align_to_entry.align_speed":0.06035,"align_to_entry.lateral_x":0.00137,"align_to_entry.lateral_y":0.01952,"approach_above.approach_height_offset":0.18876,"approach_above.arc_height":0.07163,"descend_to_contact.contact_force_threshold":8.09362,"descend_to_contact.descend_speed":0.02793,"insert_into_hole.insertion_distance":0.0548,"insert_into_hole.insertion_speed":0.03893,"insert_into_hole.max_insertion_force":22.56749},"optimized_scores":{"best_composite_score":0.19337,"best_fitness_score":0.80337,"best_task_score":0.98931},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.51346,-0.01041,0.04983],"force_p95":207.33801,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.38846,"mean_force":95.18548,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"push","tcp_position_centroid":[0.49846,-0.01055,0.05003]}],"total_contact_groups":1},"final_pose_error":0.05277,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49839,-0.01055,0.04979],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":232.38846,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":159.0,"n_steps_budget":600.0,"object_pos_end":[0.50097,0.00277,0.26559],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18562,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50034,0.00277,0.2256],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.50113,0.00631,0.14771],"object_pos_start":[0.50097,0.00277,0.26559],"object_to_goal_dist_end":0.06801,"object_to_goal_dist_start":0.18562,"object_z_max":0.26559,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50067,0.0063,0.10771],"tcp_start":[0.50034,0.00277,0.2256],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.49983,-0.01044,0.0918],"object_pos_start":[0.50113,0.00631,0.14771],"object_to_goal_dist_end":0.01576,"object_to_goal_dist_start":0.06801,"object_z_max":0.14771,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.49892,-0.01044,0.05181],"tcp_start":[0.50067,0.0063,0.10771],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":13.0,"n_steps_budget":900.0,"object_pos_end":[0.49944,-0.01055,0.09005],"object_pos_start":[0.49983,-0.01044,0.0918],"object_to_goal_dist_end":0.01458,"object_to_goal_dist_start":0.01576,"object_z_max":0.0918,"peak_contact_force":33.24971,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":232.38846,"subtask_id":"insert_peg","tcp_end":[0.49839,-0.01055,0.04979],"tcp_start":[0.49842,-0.01055,0.04985],"tcp_to_object_dist_end":0.04027,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`; realized-scene SHA-256: `f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30851,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_height_offset":0.06578,"align_to_entry.align_speed":0.09813,"align_to_entry.lateral_x":-0.00516,"align_to_entry.lateral_y":-0.02461,"approach_above.approach_height_offset":0.17076,"approach_above.arc_height":0.07328,"descend_to_contact.contact_force_threshold":4.49833,"descend_to_contact.descend_speed":0.0298,"insert_into_hole.insertion_distance":0.0595,"insert_into_hole.insertion_speed":0.01759,"insert_into_hole.max_insertion_force":31.67692},"optimized_scores":{"best_composite_score":0.41275,"best_fitness_score":0.77275,"best_task_score":0.91701},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.52033,0.03015,0.04992],"force_p95":57.19813,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.56241,"mean_force":42.33726,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"push","tcp_position_centroid":[0.50534,0.02978,0.05019]}],"total_contact_groups":1},"final_pose_error":0.05935,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50535,0.02981,0.05011],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":60.56241,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":235.0,"n_steps_budget":690.0,"object_pos_end":[0.50635,0.04392,0.25082],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17649,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50586,0.04388,0.21082],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":266.0,"n_steps_budget":810.0,"object_pos_end":[0.5023,0.01256,0.14409],"object_pos_start":[0.50635,0.04392,0.25082],"object_to_goal_dist_end":0.06535,"object_to_goal_dist_start":0.17649,"object_z_max":0.25082,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50184,0.01256,0.10409],"tcp_start":[0.50586,0.04388,0.21082],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.50626,0.02978,0.09025],"object_pos_start":[0.5023,0.01256,0.14409],"object_to_goal_dist_end":0.03211,"object_to_goal_dist_start":0.06535,"object_z_max":0.14409,"peak_contact_force":33.24971,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.50534,0.02975,0.05026],"tcp_start":[0.50184,0.01256,0.10409],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50626,0.0298,0.0902],"object_pos_start":[0.50626,0.02978,0.09025],"object_to_goal_dist_end":0.03211,"object_to_goal_dist_start":0.03211,"object_z_max":0.09025,"peak_contact_force":34.82536,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":60.56241,"subtask_id":"insert_peg","tcp_end":[0.50535,0.02981,0.05011],"tcp_start":[0.50535,0.0298,0.05014],"tcp_to_object_dist_end":0.0401,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`; realized-scene SHA-256: `586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76471,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_height_offset":0.06976,"align_to_entry.align_speed":0.06804,"align_to_entry.lateral_x":0.02976,"align_to_entry.lateral_y":-0.02397,"approach_above.approach_height_offset":0.1563,"approach_above.arc_height":0.05118,"descend_to_contact.contact_force_threshold":5.26417,"descend_to_contact.descend_speed":0.01977,"insert_into_hole.insertion_distance":0.05411,"insert_into_hole.insertion_speed":0.05,"insert_into_hole.max_insertion_force":27.13192},"optimized_scores":{"best_composite_score":0.1534,"best_fitness_score":0.7634,"best_task_score":0.88071},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.49975,0.03676,0.04978],"force_p95":130.04245,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.10912,"mean_force":74.56534,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"push","tcp_position_centroid":[0.48477,0.03607,0.04993]}],"total_contact_groups":1},"final_pose_error":0.04989,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.4847,0.03604,0.04969],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":140.10912,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":288.0,"n_steps_budget":810.0,"object_pos_end":[0.48649,0.05289,0.23509],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16441,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.48603,0.05285,0.19509],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50844,0.02084,0.1459],"object_pos_start":[0.48649,0.05289,0.23509],"object_to_goal_dist_end":0.06963,"object_to_goal_dist_start":0.16441,"object_z_max":0.23509,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50797,0.02084,0.1059],"tcp_start":[0.48603,0.05285,0.19509],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.48655,0.03603,0.0939],"object_pos_start":[0.50844,0.02084,0.1459],"object_to_goal_dist_end":0.0409,"object_to_goal_dist_start":0.06963,"object_z_max":0.1459,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.48564,0.03599,0.05391],"tcp_start":[0.50797,0.02084,0.1059],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":690.0,"object_pos_end":[0.48579,0.03611,0.08995],"object_pos_start":[0.48655,0.03603,0.0939],"object_to_goal_dist_end":0.04006,"object_to_goal_dist_start":0.0409,"object_z_max":0.0939,"peak_contact_force":33.27281,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":140.10912,"subtask_id":"insert_peg","tcp_end":[0.4847,0.03604,0.04969],"tcp_start":[0.48473,0.03605,0.04974],"tcp_to_object_dist_end":0.04027,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```