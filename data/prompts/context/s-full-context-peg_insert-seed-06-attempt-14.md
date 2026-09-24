## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2158 | 0.87 | ❌ rejected |
| 13 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1673 | 0.94 | ✅ accepted |
| 12 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.2480 | 0.93 | ❌ rejected |
| 11 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.2511 | 0.94 | ✅ accepted |
| 10 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.2497 | 0.93 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.943, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.216) — your mutation base

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
    - 0.055
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 8.0
      - 20.0
      default: 12.0
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
      distance: 0.045
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
      - 0.03
      - 0.06
      default: 0.045
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    max_insertion_force:
      type: scalar
      range:
      - 38.0
      - 40.0
      default: 39.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 39.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
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
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_into_hole** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.045, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
    - max_insertion_force: status=consumed; consumers=guards.force_guard.threshold (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=39.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: 0.216
- **task_score** (E): 0.873
- **fitness_score**: 0.776  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 0.00 | 0.1269 |
| align_to_entry | 1.00 | 0.00 | 0.0894 |
| descend_to_contact | 1.00 | 0.00 | 0.0090 |
| insert_into_hole | 0.67 | 0.33 | 0.0217 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.036, 0.181) | (0.504, -0.000, 0.340)→(0.498, 0.036, 0.221) | 0.260→0.147 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_entry | align | 1.00 / step_budget | (0.497, 0.036, 0.181)→(0.509, 0.019, 0.095) | (0.498, 0.036, 0.221)→(0.509, 0.019, 0.135) | 0.147→0.062 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_contact | contact | 1.00 / step_budget | (0.509, 0.019, 0.095)→(0.504, 0.019, 0.087) | (0.509, 0.019, 0.135)→(0.504, 0.019, 0.127) | 0.062→0.056 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_hole | push | 0.67 / step_budget | (0.503, 0.019, 0.076)→(0.500, 0.019, 0.054) | (0.504, 0.019, 0.127)→(0.501, 0.019, 0.094) | 0.056→0.031 | 0.33 / 0.333 | 17.802 | 42.954 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.942
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.942
- phase_score: 0.683
- phase_breakdown.approach_socket_score: 0.173
- phase_breakdown.insert_peg_score: 0.901

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.786
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.942
- **Median Q (composite search score)**: 0.217
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.230


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95726,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_height_offset":0.04938,"align_to_entry.align_speed":0.0805,"align_to_entry.lateral_x":0.0114,"align_to_entry.lateral_y":-0.00324,"approach_above.approach_height_offset":0.13537,"approach_above.arc_height":0.05717,"descend_to_contact.descend_speed":0.02699,"insert_into_hole.insertion_distance":0.05106,"insert_into_hole.insertion_speed":0.0226,"insert_into_hole.max_insertion_force":39.09589},"optimized_scores":{"best_composite_score":0.22639,"best_fitness_score":0.78639,"best_task_score":0.94197},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.51768,-0.01214,0.04987],"force_p95":123.63569,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.86292,"mean_force":86.2865,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"push","tcp_position_centroid":[0.50269,-0.01172,0.05013]}],"total_contact_groups":1},"final_pose_error":0.0172,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.5027,-0.01173,0.04988],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":128.86292,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":331.0,"n_steps_budget":900.0,"object_pos_end":[0.50055,0.00666,0.20497],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12515,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50006,0.00667,0.16498],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":205.0,"n_steps_budget":750.0,"object_pos_end":[0.50897,-0.01142,0.12733],"object_pos_start":[0.50055,0.00666,0.20497],"object_to_goal_dist_end":0.04951,"object_to_goal_dist_start":0.12515,"object_z_max":0.20497,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50853,-0.01141,0.08733],"tcp_start":[0.50006,0.00667,0.16498],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.5068,-0.01176,0.12409],"object_pos_start":[0.50897,-0.01142,0.12733],"object_to_goal_dist_end":0.04614,"object_to_goal_dist_start":0.04951,"object_z_max":0.12733,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.50617,-0.01175,0.0841],"tcp_start":[0.50853,-0.01141,0.08733],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,-0.01175,0.09008],"object_pos_start":[0.5068,-0.01176,0.12409],"object_to_goal_dist_end":0.01592,"object_to_goal_dist_start":0.04614,"object_z_max":0.12409,"peak_contact_force":53.40589,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":128.86292,"subtask_id":"insert_peg","tcp_end":[0.5027,-0.01173,0.04988],"tcp_start":[0.5027,-0.01173,0.04996],"tcp_to_object_dist_end":0.04021,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05085,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_height_offset":0.05837,"align_to_entry.align_speed":0.09083,"align_to_entry.lateral_x":0.01203,"align_to_entry.lateral_y":-0.00474,"approach_above.approach_height_offset":0.16348,"approach_above.arc_height":0.05888,"descend_to_contact.descend_speed":0.02594,"insert_into_hole.insertion_distance":0.04147,"insert_into_hole.insertion_speed":0.01892,"insert_into_hole.max_insertion_force":38.8221},"optimized_scores":{"best_composite_score":0.21652,"best_fitness_score":0.77652,"best_task_score":0.85447},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50919,0.03014,0.05711],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":296.0,"n_steps_budget":750.0,"object_pos_end":[0.50673,0.04852,0.23858],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16598,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50625,0.04849,0.19859],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":257.0,"n_steps_budget":840.0,"object_pos_end":[0.5168,0.03025,0.13686],"object_pos_start":[0.50673,0.04852,0.23858],"object_to_goal_dist_end":0.06656,"object_to_goal_dist_start":0.16598,"object_z_max":0.23858,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.51634,0.03023,0.09687],"tcp_start":[0.50625,0.04849,0.19859],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.51335,0.0304,0.12925],"object_pos_start":[0.5168,0.03025,0.13686],"object_to_goal_dist_end":0.0594,"object_to_goal_dist_start":0.06656,"object_z_max":0.13686,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.51266,0.03037,0.08926],"tcp_start":[0.51634,0.03023,0.09687],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.5103,0.03019,0.09709],"object_pos_start":[0.51335,0.0304,0.12925],"object_to_goal_dist_end":0.03619,"object_to_goal_dist_start":0.0594,"object_z_max":0.12925,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.50919,0.03014,0.05711],"tcp_start":[0.51266,0.03037,0.08926],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82707,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_height_offset":0.06196,"align_to_entry.align_speed":0.06703,"align_to_entry.lateral_x":0.02205,"align_to_entry.lateral_y":-0.00368,"approach_above.approach_height_offset":0.14257,"approach_above.arc_height":0.05446,"descend_to_contact.descend_speed":0.02885,"insert_into_hole.insertion_distance":0.04197,"insert_into_hole.insertion_speed":0.01638,"insert_into_hole.max_insertion_force":38.82849},"optimized_scores":{"best_composite_score":0.20436,"best_fitness_score":0.76436,"best_task_score":0.82121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48877,0.03803,0.05511],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":318.0,"n_steps_budget":870.0,"object_pos_end":[0.48609,0.05349,0.22081],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15127,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.48564,0.05345,0.18081],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":224.0,"n_steps_budget":930.0,"object_pos_end":[0.50139,0.03836,0.13943],"object_pos_start":[0.48609,0.05349,0.22081],"object_to_goal_dist_end":0.07074,"object_to_goal_dist_start":0.15127,"object_z_max":0.22081,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50093,0.03833,0.09943],"tcp_start":[0.48564,0.05345,0.18081],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":49.0,"n_steps_budget":600.0,"object_pos_end":[0.49291,0.03835,0.12774],"object_pos_start":[0.50139,0.03836,0.13943],"object_to_goal_dist_end":0.06165,"object_to_goal_dist_start":0.07074,"object_z_max":0.13943,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.49216,0.03831,0.08775],"tcp_start":[0.50093,0.03833,0.09943],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.48993,0.0381,0.09509],"object_pos_start":[0.49291,0.03835,0.12774],"object_to_goal_dist_end":0.0422,"object_to_goal_dist_start":0.06165,"object_z_max":0.12774,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.48877,0.03803,0.05511],"tcp_start":[0.49216,0.03831,0.08775],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```