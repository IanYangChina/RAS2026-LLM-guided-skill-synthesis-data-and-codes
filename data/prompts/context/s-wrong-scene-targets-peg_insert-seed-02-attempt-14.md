## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.4940 | 0.87 | ❌ rejected |
| 13 | approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.3940 | 0.87 | ❌ rejected |
| 12 | approach → contact → retract → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2125 | 0.00 | ❌ rejected |
| 11 | approach → contact → retract → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.4238 | 0.00 | ❌ rejected |
| 10 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2792 | 0.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`
- Frozen object start: [0.4809289707399447, -0.016120708526870135, 0.08]
- Frozen task target: [0.4809289707399447, -0.016120708526870135, 0.025]
- Frozen socket pose: [0.5, 0.0, 0.3] (static fixture for this episode)
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.4809289707399447, -0.016120708526870135, 0.08)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
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
  frozen_task_target: [0.4809, -0.0161, 0.08]
  frozen_socket_position: [0.4809, -0.0161, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.4809289707399447, -0.016120708526870135, 0.08]}
  frozen_targets: {'socket_entry': [0.4809289707399447, -0.016120708526870135, 0.025]}
  frozen_fixtures: {'peg_socket': [0.5, 0.0, 0.3]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.872, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4809289707399447, -0.016120708526870135, 0.08) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.3) | approach/contact targets near fixture |

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

## Current Skill (Q=0.494) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
- id: insertion_goal
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - -0.05
  weight: 0.7
phases:
- id: approach_above_socket
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
    - 0.02
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
      - 0.01
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_pre_contact
- id: contact_socket
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
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: add
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: reach_pre_contact
- id: retract_from_socket
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.015
      axis: channel_axis
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    retract_distance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: insertion_goal
- id: insert_into_hole
  type: insert
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
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    insert_distance:
      type: scalar
      range:
      - 0.03
      - 0.06
      default: 0.045
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: add
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 80.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.015
    - 0.015
    - 0.0
  subtask_id: insertion_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **contact_socket** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (add)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **retract_from_socket** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.015, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retract_speed: status=consumed; consumers=generator.speed (add)
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.045, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (add)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=80.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.015, 0.015, 0.0]

## Design Metrics

- **Composite score**: 0.494
- **task_score** (E): 0.871
- **fitness_score**: 0.591  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_socket | 1.00 | 0.00 | 0.2487 |
| contact_socket | 1.00 | 1.00 | 0.0044 |
| insert_into_hole | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_socket | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.011, 0.054) | (0.504, -0.000, 0.340)→(0.492, -0.011, 0.094) | 0.260→0.035 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_socket | contact | 1.00 / force_exceeded | (0.491, -0.011, 0.054)→(0.489, -0.012, 0.050) | (0.492, -0.011, 0.094)→(0.490, -0.012, 0.090) | 0.035→0.034 | 1.00 / 1.000 | 61.374 | 0.000 |
| insert_into_hole | insert | 0.00 / guard_failure | (0.489, -0.012, 0.050)→(0.489, -0.012, 0.050) | (0.490, -0.012, 0.090)→(0.490, -0.012, 0.090) | 0.034→0.034 | 1.00 / 1.000 | 45.378 | 210.732 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.893
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.893
- phase_score: 0.404
- phase_breakdown.insertion_goal_score: 0.224
- phase_breakdown.reach_pre_contact_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.599
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.893
- **Median Q (composite search score)**: 0.498
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.273


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6921a9025d4eafab3a26182307d104597a59aa3c28d9e7087cf253b6e9b1c7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d09be956b809b9acd01354eeb5f0494d5058516cbca42b9f2b0bee8c1b6b25a7`; realized-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,-0.01612,0.08]},{"name":"task_object","value":[0.48093,-0.01612,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.48093,-0.01612,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1,"average_solve_count":40.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_speed":0.19924,"contact_socket.contact_force_threshold":11.15296,"contact_socket.lateral_offset_x":-0.01956,"contact_socket.lateral_offset_y":0.00532,"insert_into_hole.insert_distance":0.05813,"insert_into_hole.insert_speed":0.02807,"insert_into_hole.lateral_offset_x":0.0036,"insert_into_hole.lateral_offset_y":0.00729},"optimized_scores":{"best_composite_score":0.50282,"best_fitness_score":0.59949,"best_task_score":0.89329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.49016,-0.01513,0.04979],"force_p95":173.51255,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":190.34473,"mean_force":75.4249,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.47517,-0.01486,0.04976]}],"total_contact_groups":1},"final_pose_error":0.05817,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47496,-0.01483,0.0495],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":190.34473,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":670.0,"n_steps_budget":810.0,"object_pos_end":[0.47885,-0.01522,0.09441],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02978,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.4784,-0.01521,0.05442],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.47586,-0.0149,0.09005],"object_pos_start":[0.47885,-0.01522,0.09441],"object_to_goal_dist_end":0.03009,"object_to_goal_dist_start":0.02978,"object_z_max":0.09441,"peak_contact_force":69.91615,"phase_name":"contact_socket","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_goal","tcp_end":[0.47541,-0.01489,0.05005],"tcp_start":[0.4784,-0.01521,0.05442],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.47552,-0.01485,0.0896],"object_pos_start":[0.47586,-0.0149,0.09005],"object_to_goal_dist_end":0.0302,"object_to_goal_dist_start":0.03009,"object_z_max":0.09005,"peak_contact_force":46.28004,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":190.34473,"subtask_id":"insertion_goal","tcp_end":[0.47496,-0.01483,0.0495],"tcp_start":[0.47499,-0.01483,0.04954],"tcp_to_object_dist_end":0.04011,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`; realized-scene SHA-256: `c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,-0.02106,0.08]},{"name":"task_object","value":[0.46685,-0.02106,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.46685,-0.02106,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90196,"average_solve_count":51.0,"average_success_count":51.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_speed":0.14454,"contact_socket.contact_force_threshold":8.50607,"contact_socket.lateral_offset_x":0.00654,"contact_socket.lateral_offset_y":-0.00682,"insert_into_hole.insert_distance":0.05572,"insert_into_hole.insert_speed":0.02831,"insert_into_hole.lateral_offset_x":-0.0089,"insert_into_hole.lateral_offset_y":-0.00367},"optimized_scores":{"best_composite_score":0.48107,"best_fitness_score":0.57774,"best_task_score":0.83879},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.47917,-0.02136,0.04986],"force_p95":204.48794,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":234.22982,"mean_force":92.13593,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.4642,-0.02057,0.04988]}],"total_contact_groups":1},"final_pose_error":0.05627,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46423,-0.02062,0.04976],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":234.22982,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.46561,-0.01987,0.09452],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04229,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.46518,-0.01986,0.05452],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":27.0,"n_steps_budget":600.0,"object_pos_end":[0.46467,-0.02053,0.09004],"object_pos_start":[0.46561,-0.01987,0.09452],"object_to_goal_dist_end":0.04208,"object_to_goal_dist_start":0.04229,"object_z_max":0.09452,"peak_contact_force":60.44025,"phase_name":"contact_socket","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_goal","tcp_end":[0.46422,-0.02052,0.05004],"tcp_start":[0.46518,-0.01986,0.05452],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.46465,-0.02062,0.0898],"object_pos_start":[0.46467,-0.02053,0.09004],"object_to_goal_dist_end":0.04208,"object_to_goal_dist_start":0.04208,"object_z_max":0.09004,"peak_contact_force":46.79336,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":7.0,"raw_peak_contact_force":234.22982,"subtask_id":"insertion_goal","tcp_end":[0.46423,-0.02062,0.04976],"tcp_start":[0.46421,-0.02061,0.04977],"tcp_to_object_dist_end":0.04004,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.00091,0.08]},{"name":"task_object","value":[0.53544,0.00091,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.53544,0.00091,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94697,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_speed":0.01893,"contact_socket.contact_force_threshold":4.36422,"contact_socket.lateral_offset_x":-0.00821,"contact_socket.lateral_offset_y":-0.01203,"insert_into_hole.insert_distance":0.06939,"insert_into_hole.insert_speed":0.03047,"insert_into_hole.lateral_offset_x":0.00896,"insert_into_hole.lateral_offset_y":0.0024},"optimized_scores":{"best_composite_score":0.49815,"best_fitness_score":0.59482,"best_task_score":0.8822},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.54327,0.00022,0.04976],"force_p95":186.76555,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.62003,"mean_force":82.5176,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.52827,0.0002,0.04971]}],"total_contact_groups":1},"final_pose_error":0.06951,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52815,0.00014,0.04946],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":207.62003,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.53021,0.00079,0.09299],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.03289,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.52973,0.00078,0.05299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":16.0,"n_steps_budget":600.0,"object_pos_end":[0.52894,0.00028,0.08999],"object_pos_start":[0.53021,0.00079,0.09299],"object_to_goal_dist_end":0.03062,"object_to_goal_dist_start":0.03289,"object_z_max":0.09299,"peak_contact_force":53.76517,"phase_name":"contact_socket","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_goal","tcp_end":[0.52845,0.00028,0.05],"tcp_start":[0.52973,0.00078,0.05299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.5287,0.00017,0.08955],"object_pos_start":[0.52894,0.00028,0.08999],"object_to_goal_dist_end":0.03025,"object_to_goal_dist_start":0.03062,"object_z_max":0.08999,"peak_contact_force":43.06072,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":207.62003,"subtask_id":"insertion_goal","tcp_end":[0.52815,0.00014,0.04946],"tcp_start":[0.52816,0.00015,0.0495],"tcp_to_object_dist_end":0.04009,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```