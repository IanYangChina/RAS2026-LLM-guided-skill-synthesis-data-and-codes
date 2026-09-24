## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1772 | 0.27 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2392 | 0.40 | ✅ accepted |
| 11 | approach → align → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | -0.0616 | 0.19 | ❌ rejected |
| 10 | approach → align → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | -0.0204 | 0.21 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.2085 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.177) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.06
  weight: 0.3
- id: place_at_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: bilateral_grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
- id: approach_goal
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height_goal:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: transport_grasp_guard
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: abort
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_at_goal
- id: release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
- id: retract
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height_goal: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=transport_grasp_guard, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.05
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.177
- **task_score** (E): 0.269
- **fitness_score**: 0.607  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1648 |
| descend_to_grasp | 1.00 | 1.00 | 0.0961 |
| grasp | 0.00 | 1.00 | 0.0000 |
| lift | 0.33 | 1.00 | 0.1380 |
| approach_goal | 0.00 | 1.00 | 0.0445 |
| descend_place | 0.33 | 1.00 | 0.1043 |
| release | 1.00 | 1.00 | 0.0225 |
| retract | 1.00 | 1.00 | 0.1359 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.022, 0.141) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.022, 0.141)→(0.506, 0.022, 0.045) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 0.00 / guard_failure | (0.501, 0.022, 0.040)→(0.501, 0.022, 0.040) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 44.000 | 0.139 | 0.184 |
| lift | lift | 0.33 / step_budget | (0.501, 0.022, 0.040)→(0.497, 0.022, 0.178) | (0.511, 0.022, 0.026)→(0.510, 0.022, 0.157) | 0.273→0.224 | 1.00 / 29.333 | 0.094 | 0.559 |
| approach_goal | approach | 0.00 / guard_failure | (0.497, 0.022, 0.178)→(0.521, 0.056, 0.186) | (0.510, 0.022, 0.157)→(0.532, 0.056, 0.160) | 0.224→0.182 | 1.00 / 22.000 | 0.003 | 0.213 |
| descend_place | descend | 0.33 / step_budget | (0.521, 0.056, 0.186)→(0.571, 0.140, 0.194) | (0.532, 0.056, 0.160)→(0.561, 0.120, 0.058) | 0.182→0.179 | 1.00 / 7.333 | 0.119 | 1.272 |
| release | release | 1.00 / step_budget | (0.571, 0.140, 0.194)→(0.566, 0.139, 0.215) | (0.561, 0.120, 0.058)→(0.565, 0.122, 0.016) | 0.179→0.205 | 1.00 / 4.000 | 0.123 | 0.625 |
| retract | retract | 1.00 / step_budget | (0.566, 0.139, 0.215)→(0.564, 0.138, 0.351) | (0.565, 0.122, 0.016)→(0.565, 0.122, 0.016) | 0.205→0.205 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.398
- phase_score: 0.472
- phase_breakdown.reach_object_score: 0.433
- phase_breakdown.place_at_goal_score: 0.489
- grasp_place_fitness: 0.668

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.668
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.398
- **Median Q (composite search score)**: 0.156
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.568


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89157,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_height_goal":0.08745,"approach_object.approach_height":0.11057,"descend_place.place_z_offset":0.04325,"descend_to_grasp.descend_z":0.02503,"lift.lift_height":0.21345},"optimized_scores":{"best_composite_score":0.23802,"best_fitness_score":0.66802,"best_task_score":0.39808},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2996.0,"contact_point_centroid":[0.59364,0.13646,-0.00237],"force_p95":0.12988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67863,"mean_force":0.13973,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59947,0.14714,0.18954]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.50981,0.03832,-0.00116],"force_p95":0.36619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51824,"mean_force":0.06518,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50117,0.03873,0.04487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17295.0,"contact_point_centroid":[0.50099,0.05754,0.11922],"force_p95":0.08884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30689,"mean_force":0.05946,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49873,0.03854,0.11714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17068.0,"contact_point_centroid":[0.5008,0.01958,0.11788],"force_p95":0.09385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29554,"mean_force":0.05953,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49872,0.03853,0.11575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9399.0,"contact_point_centroid":[0.53596,0.05496,0.2068],"force_p95":0.14435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24248,"mean_force":0.08237,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52994,0.07358,0.2069]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51252,0.03961,-0.00209],"force_p95":0.14371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1923,"mean_force":0.12951,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50322,0.0389,0.04362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.57029,0.12424,0.20698],"force_p95":0.1401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18367,"mean_force":0.03773,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56408,0.1092,0.21198]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10042.0,"contact_point_centroid":[0.53703,0.09304,0.20698],"force_p95":0.11804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18258,"mean_force":0.07706,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53085,0.07452,0.20707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5.0,"contact_point_centroid":[0.57095,0.09282,0.20547],"force_p95":0.17657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1804,"mean_force":0.1405,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56345,0.10857,0.21265]},{"body_a":"world","body_b":"grasp_target","contact_count":3364.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50296,0.01937,0.21676]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50637,0.03852,0.08858]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59368,0.13648,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61789,0.16832,0.18048]},{"body_a":"world","body_b":"grasp_target","contact_count":3492.0,"contact_point_centroid":[0.59368,0.13648,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61387,0.16695,0.2647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5823.0,"contact_point_centroid":[0.50291,0.01968,0.045],"force_p95":0.07071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12002,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50272,0.03886,0.04307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5928.0,"contact_point_centroid":[0.50289,0.05807,0.04491],"force_p95":0.07108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0743,"mean_force":0.04501,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50272,0.03886,0.04307]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2936.0,"contact_point_centroid":[0.60192,0.14913,0.1909],"force_p95":0.01132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01063,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60144,0.14911,0.18868]}],"total_contact_groups":17},"final_pose_error":0.01525,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59368,0.13648,0.01602],"final_tcp_position":[0.61468,0.16712,0.33469],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.67863,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":842.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3364.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50797,0.03783,0.14134],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50752,0.03926,0.04845],"tcp_start":[0.50797,0.03783,0.14134],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03911,0.02571],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21282,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14053,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13555.0,"raw_peak_contact_force":0.1923,"tcp_end":[0.5027,0.03886,0.04304],"tcp_start":[0.5027,0.03886,0.04304],"tcp_to_object_dist_end":0.01987,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51153,0.03873,0.18051],"object_pos_start":[0.51243,0.0391,0.02573],"object_to_goal_dist_end":0.18063,"object_to_goal_dist_start":0.21282,"object_z_max":0.18033,"peak_contact_force":0.09294,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34502.0,"raw_peak_contact_force":0.51824,"tcp_end":[0.49914,0.03857,0.20571],"tcp_start":[0.5027,0.03886,0.04304],"tcp_to_object_dist_end":0.02808,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.56936,0.10982,0.17829],"object_pos_start":[0.51153,0.03873,0.18051],"object_to_goal_dist_end":0.09179,"object_to_goal_dist_start":0.18063,"object_z_max":0.18063,"peak_contact_force":0.01017,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19441.0,"raw_peak_contact_force":0.24248,"tcp_end":[0.56344,0.10856,0.21266],"tcp_start":[0.49914,0.03857,0.20571],"tcp_to_object_dist_end":0.0349,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.59368,0.13648,0.01602],"object_pos_start":[0.56936,0.10982,0.17829],"object_to_goal_dist_end":0.13817,"object_to_goal_dist_start":0.09179,"object_z_max":0.17829,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6014.0,"raw_peak_contact_force":1.67863,"subtask_id":"place_at_goal","tcp_end":[0.62191,0.16953,0.18022],"tcp_start":[0.56344,0.10856,0.21266],"tcp_to_object_dist_end":0.16985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59368,0.13648,0.01602],"object_pos_start":[0.59368,0.13648,0.01602],"object_to_goal_dist_end":0.13817,"object_to_goal_dist_start":0.13817,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61635,0.16779,0.19984],"tcp_start":[0.62191,0.16953,0.18022],"tcp_to_object_dist_end":0.18784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.59368,0.13648,0.01602],"object_pos_start":[0.59368,0.13648,0.01602],"object_to_goal_dist_end":0.13817,"object_to_goal_dist_start":0.13817,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61468,0.16712,0.33469],"tcp_start":[0.61635,0.16779,0.19984],"tcp_to_object_dist_end":0.32083,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77576,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_height_goal":0.09528,"approach_object.approach_height":0.06547,"descend_place.place_z_offset":0.02233,"descend_to_grasp.descend_z":0.02122,"lift.lift_height":0.2457},"optimized_scores":{"best_composite_score":0.13723,"best_fitness_score":0.56723,"best_task_score":0.1961},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1767.0,"contact_point_centroid":[0.52636,0.12565,-0.00261],"force_p95":0.25818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88616,"mean_force":0.14936,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52152,0.13738,0.22226]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.47981,0.04704,-0.00117],"force_p95":0.31621,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51991,"mean_force":0.06163,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4717,0.04743,0.04482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17254.0,"contact_point_centroid":[0.47173,0.0662,0.11897],"force_p95":0.08857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30469,"mean_force":0.05976,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46931,0.0472,0.11687]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16920.0,"contact_point_centroid":[0.47145,0.02825,0.11757],"force_p95":0.09448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2917,"mean_force":0.05998,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46931,0.0472,0.1154]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":735.0,"contact_point_centroid":[0.47707,0.03216,0.20635],"force_p95":0.10622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24377,"mean_force":0.07691,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47091,0.05098,0.20539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4522.0,"contact_point_centroid":[0.49141,0.06165,0.2065],"force_p95":0.13479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23141,"mean_force":0.09246,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.4855,0.08001,0.20848]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48272,0.04859,-0.00212],"force_p95":0.14968,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20928,"mean_force":0.13121,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47361,0.04763,0.04344]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4609.0,"contact_point_centroid":[0.49193,0.09918,0.20631],"force_p95":0.12766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19586,"mean_force":0.09177,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48606,0.08088,0.20871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.47747,0.06968,0.20732],"force_p95":0.09052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16404,"mean_force":0.06675,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47089,0.05091,0.20537]},{"body_a":"world","body_b":"grasp_target","contact_count":3876.0,"contact_point_centroid":[0.4827,0.04873,-0.00196],"force_p95":0.12481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48824,0.02358,0.19561]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5816.0,"contact_point_centroid":[0.47334,0.0284,0.04491],"force_p95":0.07181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12775,"mean_force":0.04495,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47315,0.04758,0.04296]},{"body_a":"world","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47704,0.04719,0.07065]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52639,0.12568,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53082,0.15618,0.22976]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.52639,0.12568,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52757,0.15508,0.31682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5956.0,"contact_point_centroid":[0.47332,0.0668,0.0448],"force_p95":0.07226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07503,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47315,0.04758,0.04297]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1667.0,"contact_point_centroid":[0.52353,0.13983,0.22515],"force_p95":0.01176,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01514,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52307,0.13982,0.22287]}],"total_contact_groups":17},"final_pose_error":0.0135,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52639,0.12568,0.01602],"final_tcp_position":[0.52826,0.15522,0.38673],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.88616,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":970.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3876.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47915,0.04652,0.09814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47778,0.04804,0.0478],"tcp_start":[0.47915,0.04652,0.09814],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48263,0.04792,0.02564],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29077,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14518,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13576.0,"raw_peak_contact_force":0.20928,"tcp_end":[0.47313,0.04758,0.04294],"tcp_start":[0.47313,0.04758,0.04294],"tcp_to_object_dist_end":0.01973,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48207,0.04739,0.17896],"object_pos_start":[0.48263,0.0479,0.02566],"object_to_goal_dist_end":0.21341,"object_to_goal_dist_start":0.29077,"object_z_max":0.17878,"peak_contact_force":0.09386,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34308.0,"raw_peak_contact_force":0.51991,"tcp_end":[0.46964,0.04724,0.20446],"tcp_start":[0.47313,0.04758,0.04294],"tcp_to_object_dist_end":0.02837,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.48496,0.05499,0.18016],"object_pos_start":[0.48207,0.04739,0.17896],"object_to_goal_dist_end":0.20531,"object_to_goal_dist_start":0.21341,"object_z_max":0.18012,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1571.0,"raw_peak_contact_force":0.24377,"tcp_end":[0.47231,0.05495,0.2064],"tcp_start":[0.46964,0.04724,0.20446],"tcp_to_object_dist_end":0.02913,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52639,0.12568,0.01602],"object_pos_start":[0.48496,0.05499,0.18016],"object_to_goal_dist_end":0.24437,"object_to_goal_dist_start":0.20531,"object_z_max":0.183,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12565.0,"raw_peak_contact_force":1.88616,"subtask_id":"place_at_goal","tcp_end":[0.53409,0.15705,0.22719],"tcp_start":[0.47231,0.05495,0.2064],"tcp_to_object_dist_end":0.21362,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52639,0.12568,0.01602],"object_pos_start":[0.52639,0.12568,0.01602],"object_to_goal_dist_end":0.24437,"object_to_goal_dist_start":0.24437,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52959,0.15575,0.25016],"tcp_start":[0.53409,0.15705,0.22719],"tcp_to_object_dist_end":0.23609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.52639,0.12568,0.01602],"object_pos_start":[0.52639,0.12568,0.01602],"object_to_goal_dist_end":0.24437,"object_to_goal_dist_start":0.24437,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52826,0.15522,0.38673],"tcp_start":[0.52959,0.15575,0.25016],"tcp_to_object_dist_end":0.37189,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87234,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_height_goal":0.13372,"approach_object.approach_height":0.14933,"descend_place.place_z_offset":0.03206,"descend_to_grasp.descend_z":0.017,"lift.lift_height":0.10215},"optimized_scores":{"best_composite_score":0.1562,"best_fitness_score":0.5862,"best_task_score":0.21375},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.57406,0.103,-0.00391],"force_p95":0.96339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63013,"mean_force":0.21668,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55172,0.09348,0.17895]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.53417,-0.02104,-0.00113],"force_p95":0.42951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6396,"mean_force":0.08225,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5251,-0.02105,0.03559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11149.0,"contact_point_centroid":[0.52313,-0.04007,0.07764],"force_p95":0.08087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31357,"mean_force":0.05347,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52243,-0.02098,0.07578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10752.0,"contact_point_centroid":[0.52312,-0.00188,0.07818],"force_p95":0.08187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31329,"mean_force":0.05497,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52244,-0.02098,0.07598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10877.0,"contact_point_centroid":[0.54349,0.02803,0.15219],"force_p95":0.14908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25085,"mean_force":0.08367,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53927,0.0466,0.15253]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11624.0,"contact_point_centroid":[0.54482,0.06684,0.15285],"force_p95":0.12977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17183,"mean_force":0.07836,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53993,0.04842,0.1533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3704.0,"contact_point_centroid":[0.5275,-0.02588,0.1317],"force_p95":0.10466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15145,"mean_force":0.07236,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52393,-0.00719,0.13087]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53701,-0.02126,-0.00204],"force_p95":0.13192,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14967,"mean_force":0.12594,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52727,-0.02109,0.0345]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51647,-0.01129,0.23062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3684.0,"contact_point_centroid":[0.5279,0.01147,0.13172],"force_p95":0.10138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13804,"mean_force":0.07286,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52393,-0.0072,0.13086]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.57413,0.10276,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12384,"mean_force":0.12264,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54871,0.09292,0.26238]},{"body_a":"world","body_b":"grasp_target","contact_count":3832.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52973,-0.02033,0.09795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5842.0,"contact_point_centroid":[0.52693,-0.0019,0.0358],"force_p95":0.0682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.103,"mean_force":0.04499,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52675,-0.02108,0.03389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5884.0,"contact_point_centroid":[0.52695,-0.04027,0.03577],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08859,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52675,-0.02108,0.03389]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.5627,0.10858,0.16739],"force_p95":0.07417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07991,"mean_force":0.02358,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5569,0.09445,0.17293]}],"total_contact_groups":15},"final_pose_error":0.01378,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57413,0.10276,0.01602],"final_tcp_position":[0.54935,0.093,0.33226],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.63013,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52983,-0.01921,0.1848],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3832.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53181,-0.02118,0.03977],"tcp_start":[0.52983,-0.01921,0.1848],"tcp_to_object_dist_end":0.01471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02111,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31668,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13104,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13530.0,"raw_peak_contact_force":0.14967,"tcp_end":[0.52672,-0.02108,0.03386],"tcp_start":[0.52672,-0.02108,0.03386],"tcp_to_object_dist_end":0.01295,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.53641,-0.02087,0.11059],"object_pos_start":[0.5369,-0.02111,0.02587],"object_to_goal_dist_end":0.27686,"object_to_goal_dist_start":0.31667,"object_z_max":0.11048,"peak_contact_force":0.09666,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22046.0,"raw_peak_contact_force":0.6396,"tcp_end":[0.52249,-0.02098,0.12358],"tcp_start":[0.52672,-0.02108,0.03386],"tcp_to_object_dist_end":0.01905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.54041,0.00375,0.12258],"object_pos_start":[0.53641,-0.02087,0.11059],"object_to_goal_dist_end":0.24952,"object_to_goal_dist_start":0.27686,"object_z_max":0.12253,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7388.0,"raw_peak_contact_force":0.15145,"tcp_end":[0.52704,0.00384,0.13926],"tcp_start":[0.52249,-0.02098,0.12358],"tcp_to_object_dist_end":0.02139,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56321,0.09711,0.1417],"object_pos_start":[0.54041,0.00375,0.12258],"object_to_goal_dist_end":0.15364,"object_to_goal_dist_start":0.24952,"object_z_max":0.14538,"peak_contact_force":0.11122,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22501.0,"raw_peak_contact_force":0.25085,"subtask_id":"place_at_goal","tcp_end":[0.557,0.09436,0.1731],"tcp_start":[0.52704,0.00384,0.13926],"tcp_to_object_dist_end":0.03212,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57411,0.10267,0.01601],"object_pos_start":[0.56321,0.09711,0.1417],"object_to_goal_dist_end":0.23149,"object_to_goal_dist_start":0.15364,"object_z_max":0.1417,"peak_contact_force":0.12385,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":540.0,"raw_peak_contact_force":1.63013,"tcp_end":[0.55138,0.09342,0.19588],"tcp_start":[0.557,0.09436,0.1731],"tcp_to_object_dist_end":0.18153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.57413,0.10276,0.01602],"object_pos_start":[0.57411,0.10267,0.01601],"object_to_goal_dist_end":0.23144,"object_to_goal_dist_start":0.23149,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.12384,"tcp_end":[0.54935,0.093,0.33226],"tcp_start":[0.55138,0.09342,0.19588],"tcp_to_object_dist_end":0.31736,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```