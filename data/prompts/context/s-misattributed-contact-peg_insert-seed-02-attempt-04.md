## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3243 | 0.85 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 7 | 0.2816 | 0.85 | ✅ accepted |
| 2 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ❌ rejected |
| 1 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ❌ rejected |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.4809289707399447, -0.016120708526870135, 0.08]
- Frozen socket pose: [0.4809289707399447, -0.016120708526870135, 0.025] (static fixture for this episode)
- Goal object position: (0.4809289707399447, -0.016120708526870135, 0.025)
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
  frozen_task_target: [0.4809, -0.0161, 0.08]
  frozen_socket_position: [0.4809, -0.0161, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.4809289707399447, -0.016120708526870135, 0.08]}
  frozen_fixtures: {'peg_socket': [0.4809289707399447, -0.016120708526870135, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.854, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.4809289707399447, -0.016120708526870135, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.4809289707399447, -0.016120708526870135, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.324) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: reach_goal
  target_entity: object
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_entry
- id: descend_into_hole
  type: push
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
    - 0.055
    offset_along_axis:
      distance: 0.045
      axis: channel_axis
      mode: add_to_offset
      sign: positive
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
    descend_depth:
      type: scalar
      range:
      - 0.03
      - 0.06
      default: 0.045
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: reach_goal
- id: final_insert
  type: push
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
      distance: 0.055
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    final_depth:
      type: scalar
      range:
      - 0.04
      - 0.07
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    final_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    final_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    force_limit:
      type: scalar
      range:
      - 20.0
      - 60.0
      default: 40.0
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_into_hole** (`push`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.045, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **final_insert** (`push`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - final_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - final_speed: status=consumed; consumers=generator.speed (replace)
    - final_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - force_limit: status=consumed; consumers=guards.force_limit.threshold (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: 0.324
- **task_score** (E): 0.854
- **fitness_score**: 0.854  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_socket | 1.00 | 0.67 | 0.1966 |
| descend_into_hole | 0.33 | 1.00 | 0.0162 |
| final_insert | 0.00 | 0.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_socket | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.011, 0.107) | (0.504, -0.000, 0.340)→(0.492, -0.011, 0.147) | 0.260→0.074 | 0.67 / 0.667 | 84.120 | 185.746 |
| descend_into_hole | push | 0.33 / guard_failure | (0.491, -0.012, 0.067)→(0.491, -0.012, 0.051) | (0.492, -0.011, 0.147)→(0.491, -0.012, 0.091) | 0.074→0.035 | 1.00 / 1.000 | 43.718 | 108.409 |
| final_insert | push | 0.00 / guard_failure | (0.490, -0.012, 0.049)→(0.490, -0.012, 0.049) | (0.491, -0.012, 0.091)→(0.491, -0.012, 0.089) | 0.035→0.035 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.878
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.878
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.878
- **Median Q (composite search score)**: 0.339
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.336


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
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32927,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.01332,"approach_socket.approach_speed":0.11959,"approach_socket.approach_tolerance":0.01223,"descend_into_hole.descend_depth":0.04486,"descend_into_hole.descend_speed":0.09993,"descend_into_hole.descend_tolerance":0.02252,"final_insert.final_depth":0.05872,"final_insert.final_speed":0.01104,"final_insert.final_tolerance":0.01064,"final_insert.force_limit":27.27499},"optimized_scores":{"best_composite_score":0.34826,"best_fitness_score":0.87826,"best_task_score":0.87826},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.49091,-0.01635,0.04992],"force_p95":148.01872,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.14102,"mean_force":90.78,"phase_index":2.0,"phase_name":"final_insert","phase_type":"push","tcp_position_centroid":[0.47593,-0.01572,0.05004]}],"total_contact_groups":1},"final_pose_error":0.02902,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47592,-0.01572,0.04987],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":157.14102,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.47941,-0.01499,0.14288],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06785,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.47898,-0.01498,0.10289],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":100.0,"n_steps_budget":600.0,"object_pos_end":[0.47815,-0.01571,0.09487],"object_pos_start":[0.47941,-0.01499,0.14288],"object_to_goal_dist_end":0.03074,"object_to_goal_dist_start":0.06785,"object_z_max":0.14288,"peak_contact_force":49.28095,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":157.14102,"subtask_id":"reach_goal","tcp_end":[0.47775,-0.0157,0.05487],"tcp_start":[0.47898,-0.01498,0.10289],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.47644,-0.01573,0.09],"object_pos_start":[0.47815,-0.01571,0.09487],"object_to_goal_dist_end":0.03004,"object_to_goal_dist_start":0.03074,"object_z_max":0.09487,"peak_contact_force":0.0,"phase_name":"final_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.47592,-0.01572,0.04987],"tcp_start":[0.47593,-0.01572,0.04992],"tcp_to_object_dist_end":0.04014,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`; realized-scene SHA-256: `c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2,"average_solve_count":50.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.01011,"approach_socket.approach_speed":0.18004,"approach_socket.approach_tolerance":0.01835,"descend_into_hole.descend_depth":0.05552,"descend_into_hole.descend_speed":0.07224,"descend_into_hole.descend_tolerance":0.02862,"final_insert.final_depth":0.04959,"final_insert.final_speed":0.03342,"final_insert.final_tolerance":0.01559,"final_insert.force_limit":29.95391},"optimized_scores":{"best_composite_score":0.28614,"best_fitness_score":0.81614,"best_task_score":0.81614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.47902,-0.02095,0.04987],"force_p95":291.03686,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.46905,"mean_force":206.14716,"phase_index":1.0,"phase_name":"descend_into_hole","phase_type":"push","tcp_position_centroid":[0.46404,-0.02044,0.04988]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.47915,-0.02078,0.04953],"force_p95":74.27378,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.54351,"mean_force":56.24738,"phase_index":2.0,"phase_name":"final_insert","phase_type":"push","tcp_position_centroid":[0.46416,-0.02046,0.04919]}],"total_contact_groups":2},"final_pose_error":0.01879,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46423,-0.02047,0.04901],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":300.46905,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":558.0,"n_steps_budget":750.0,"object_pos_end":[0.46627,-0.01958,0.13983],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07142,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":111.82528,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":300.46905,"subtask_id":"approach_entry","tcp_end":[0.46583,-0.01957,0.09984],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":106.0,"n_steps_budget":660.0,"object_pos_end":[0.46443,-0.02045,0.08966],"object_pos_start":[0.46627,-0.01958,0.13983],"object_to_goal_dist_end":0.04215,"object_to_goal_dist_start":0.07142,"object_z_max":0.13983,"peak_contact_force":38.35244,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":76.54351,"subtask_id":"reach_goal","tcp_end":[0.4641,-0.02045,0.04936],"tcp_start":[0.46405,-0.02044,0.04967],"tcp_to_object_dist_end":0.0403,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.46451,-0.02046,0.08916],"object_pos_start":[0.46447,-0.02046,0.08936],"object_to_goal_dist_end":0.04198,"object_to_goal_dist_start":0.04205,"object_z_max":0.08936,"peak_contact_force":0.0,"phase_name":"final_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.46423,-0.02047,0.04901],"tcp_start":[0.46421,-0.02046,0.04905],"tcp_to_object_dist_end":0.04016,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16842,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.02895,"approach_socket.approach_speed":0.15538,"approach_socket.approach_tolerance":0.01511,"descend_into_hole.descend_depth":0.05999,"descend_into_hole.descend_speed":0.02781,"descend_into_hole.descend_tolerance":0.02207,"final_insert.final_depth":0.05702,"final_insert.final_speed":0.02455,"final_insert.final_tolerance":0.01577,"final_insert.force_limit":49.901},"optimized_scores":{"best_composite_score":0.33857,"best_fitness_score":0.86857,"best_task_score":0.86857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.54509,0.00092,0.04968],"force_p95":250.95726,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.76892,"mean_force":198.65226,"phase_index":1.0,"phase_name":"descend_into_hole","phase_type":"push","tcp_position_centroid":[0.53009,0.0008,0.04953]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.54529,0.00114,0.0494],"force_p95":88.42427,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.54115,"mean_force":65.14488,"phase_index":2.0,"phase_name":"final_insert","phase_type":"push","tcp_position_centroid":[0.5303,0.00079,0.04895]}],"total_contact_groups":2},"final_pose_error":0.02633,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.53044,0.00078,0.04883],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":256.76892,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":553.0,"n_steps_budget":810.0,"object_pos_end":[0.53012,0.00079,0.15683],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08253,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":140.5356,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":256.76892,"subtask_id":"approach_entry","tcp_end":[0.52964,0.00079,0.11683],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.53059,0.0008,0.08933],"object_pos_start":[0.53012,0.00079,0.15683],"object_to_goal_dist_end":0.03199,"object_to_goal_dist_start":0.08253,"object_z_max":0.15683,"peak_contact_force":43.52111,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":91.54115,"subtask_id":"reach_goal","tcp_end":[0.53021,0.0008,0.04907],"tcp_start":[0.53012,0.0008,0.04933],"tcp_to_object_dist_end":0.04026,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":690.0,"object_pos_end":[0.53073,0.0008,0.08892],"object_pos_start":[0.53066,0.0008,0.08907],"object_to_goal_dist_end":0.03201,"object_to_goal_dist_start":0.03198,"object_z_max":0.08907,"peak_contact_force":0.0,"phase_name":"final_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.53044,0.00078,0.04883],"tcp_start":[0.53038,0.00078,0.04887],"tcp_to_object_dist_end":0.0401,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```