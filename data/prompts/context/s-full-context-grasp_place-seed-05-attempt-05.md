## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.0215 | 0.28 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1979 | 0.22 | ✅ accepted |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |
| 1 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
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

## Current Skill (Q=-0.022) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  weight: 0.3
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
  target_entity: object
  weight: 0.3
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
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
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp_object
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_timeout:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: grasp_object
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
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
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    move_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_place
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: release_object
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
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_after_place
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
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - move_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.022
- **task_score** (E): 0.280
- **fitness_score**: 0.508  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_grasp | 1.00 | 1.00 | 0.0737 |
| grasp_object | 1.00 | 1.00 | 0.0120 |
| lift_object | 1.00 | 1.00 | 0.0712 |
| approach_goal | 1.00 | 1.00 | 0.2049 |
| descend_to_place | 1.00 | 1.00 | 0.0713 |
| release_object | 1.00 | 1.00 | 0.0213 |
| retract_after_place | 1.00 | 1.00 | 0.0615 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.510, 0.018, 0.064) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.064)→(0.502, 0.017, 0.055) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 26.667 | 0.144 | 0.193 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.055)→(0.510, 0.018, 0.126) | (0.516, 0.018, 0.026)→(0.517, 0.018, 0.090) | 0.236→0.209 | 1.00 / 20.333 | 0.112 | 0.278 |
| approach_goal | approach | 1.00 / step_budget | (0.510, 0.018, 0.126)→(0.591, 0.159, 0.241) | (0.517, 0.018, 0.090)→(0.535, 0.059, 0.016) | 0.209→0.208 | 1.00 / 8.000 | 0.123 | 1.220 |
| descend_to_place | descend | 1.00 / step_budget | (0.591, 0.159, 0.241)→(0.599, 0.175, 0.173) | (0.535, 0.059, 0.016)→(0.535, 0.059, 0.016) | 0.208→0.208 | 1.00 / 8.333 | 91003.082 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.599, 0.175, 0.173)→(0.593, 0.173, 0.193) | (0.535, 0.059, 0.016)→(0.535, 0.059, 0.016) | 0.208→0.208 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.593, 0.173, 0.193)→(0.602, 0.178, 0.254) | (0.535, 0.059, 0.016)→(0.535, 0.059, 0.016) | 0.208→0.208 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.436
- phase_score: 0.693
- phase_breakdown.grasp_object_score: 0.571
- phase_breakdown.reach_goal_score: 0.822
- phase_breakdown.approach_object_score: 0.821
- phase_breakdown.lift_object_score: 0.555
- grasp_place_fitness: 0.670

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.670
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.436
- **Median Q (composite search score)**: -0.013
- **K-run variance**: 0.0184
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.214


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.move_speed":0.21595,"approach_object.approach_speed":0.24773,"descend_to_grasp.descend_speed":0.03426,"descend_to_place.place_speed":0.06536,"grasp_object.grasp_timeout":0.82804,"lift_object.lift_height":0.1379,"release_object.release_timeout":0.26426},"optimized_scores":{"best_composite_score":0.14018,"best_fitness_score":0.67018,"best_task_score":0.43606},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2671.0,"contact_point_centroid":[0.56004,0.10573,-0.0023],"force_p95":0.12556,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22509,"mean_force":0.13643,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56883,0.12064,0.17919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5945.0,"contact_point_centroid":[0.52235,0.01108,0.09578],"force_p95":0.13227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30459,"mean_force":0.09756,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51907,0.02943,0.09921]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6124.0,"contact_point_centroid":[0.5222,0.04772,0.09573],"force_p95":0.13123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27072,"mean_force":0.09472,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51911,0.02943,0.09918]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.5291,0.02893,-0.0012],"force_p95":0.21283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27005,"mean_force":0.04631,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51574,0.02943,0.05636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2246.0,"contact_point_centroid":[0.53849,0.03118,0.14925],"force_p95":0.1522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25384,"mean_force":0.10532,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53277,0.04946,0.15375]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2463.0,"contact_point_centroid":[0.53861,0.06837,0.1497],"force_p95":0.11595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22659,"mean_force":0.09463,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53317,0.05027,0.15404]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03071,-0.00209],"force_p95":0.1517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20474,"mean_force":0.1297,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5181,0.02961,0.05591]},{"body_a":"world","body_b":"grasp_target","contact_count":1884.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51099,0.01392,0.21769]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52327,0.02903,0.10047]},{"body_a":"world","body_b":"grasp_target","contact_count":984.0,"contact_point_centroid":[0.56007,0.10576,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59234,0.16905,0.15509]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56007,0.10576,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59053,0.17331,0.11563]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.56007,0.10576,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59127,0.17436,0.16298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2482.0,"contact_point_centroid":[0.51834,0.01078,0.05182],"force_p95":0.10472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11102,"mean_force":0.08103,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51695,0.02953,0.05456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2992.0,"contact_point_centroid":[0.51745,0.04818,0.05143],"force_p95":0.09425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09441,"mean_force":0.0692,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51696,0.02953,0.05457]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2486.0,"contact_point_centroid":[0.57134,0.12551,0.18327],"force_p95":0.01135,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01074,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57134,0.1255,0.18099]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1042.0,"contact_point_centroid":[0.59238,0.16906,0.15741],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59233,0.16904,0.1551]}],"total_contact_groups":17},"final_pose_error":0.01409,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56007,0.10576,0.01602],"final_tcp_position":[0.59705,0.17698,0.19482],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.22509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5242,0.0282,0.13715],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52493,0.03005,0.06409],"tcp_start":[0.5242,0.0282,0.13715],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02989,0.02568],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18426,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14802,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7274.0,"raw_peak_contact_force":0.20474,"subtask_id":"grasp_object","tcp_end":[0.51692,0.02953,0.05453],"tcp_start":[0.52493,0.03005,0.06409],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":607.0,"n_steps_budget":690.0,"object_pos_end":[0.53167,0.02987,0.11466],"object_pos_start":[0.53046,0.02989,0.02568],"object_to_goal_dist_end":0.16443,"object_to_goal_dist_start":0.18426,"object_z_max":0.11455,"peak_contact_force":0.11364,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12229.0,"raw_peak_contact_force":0.30459,"subtask_id":"lift_object","tcp_end":[0.52567,0.02961,0.15095],"tcp_start":[0.51692,0.02953,0.05453],"tcp_to_object_dist_end":0.03678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56007,0.10576,0.01602],"object_pos_start":[0.53167,0.02987,0.11466],"object_to_goal_dist_end":0.1245,"object_to_goal_dist_start":0.16443,"object_z_max":0.12034,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9866.0,"raw_peak_contact_force":1.22509,"subtask_id":"reach_goal","tcp_end":[0.59132,0.16435,0.19527],"tcp_start":[0.52567,0.02961,0.15095],"tcp_to_object_dist_end":0.19116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":246.0,"n_steps_budget":1000.0,"object_pos_end":[0.56007,0.10576,0.01602],"object_pos_start":[0.56007,0.10576,0.01602],"object_to_goal_dist_end":0.1245,"object_to_goal_dist_start":0.1245,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2026.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59556,0.17483,0.11492],"tcp_start":[0.59132,0.16435,0.19527],"tcp_to_object_dist_end":0.12575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56007,0.10576,0.01602],"object_pos_start":[0.56007,0.10576,0.01602],"object_to_goal_dist_end":0.1245,"object_to_goal_dist_start":0.1245,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58868,0.17269,0.13551],"tcp_start":[0.59556,0.17483,0.11492],"tcp_to_object_dist_end":0.13992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.56007,0.10576,0.01602],"object_pos_start":[0.56007,0.10576,0.01602],"object_to_goal_dist_end":0.1245,"object_to_goal_dist_start":0.1245,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59705,0.17698,0.19482],"tcp_start":[0.58868,0.17269,0.13551],"tcp_to_object_dist_end":0.19599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.move_speed":0.33346,"approach_object.approach_speed":0.19772,"descend_to_grasp.descend_speed":0.04201,"descend_to_place.place_speed":0.04205,"grasp_object.grasp_timeout":0.65295,"lift_object.lift_height":0.1428,"release_object.release_timeout":0.23424},"optimized_scores":{"best_composite_score":-0.01306,"best_fitness_score":0.51694,"best_task_score":0.13125},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3176.0,"contact_point_centroid":[0.51835,0.00251,-0.00228],"force_p95":0.12458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45379,"mean_force":0.13435,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54196,0.08948,0.24955]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6337.0,"contact_point_centroid":[0.49572,-0.03349,0.09836],"force_p95":0.12691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27507,"mean_force":0.09456,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49292,-0.01526,0.1022]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5954.0,"contact_point_centroid":[0.49543,0.00309,0.09703],"force_p95":0.13749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2747,"mean_force":0.10016,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4928,-0.01526,0.10086]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.50251,-0.01515,-0.0011],"force_p95":0.22789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26907,"mean_force":0.04081,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48995,-0.01524,0.05759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1089.0,"contact_point_centroid":[0.50601,0.01211,0.157],"force_p95":0.16935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25547,"mean_force":0.10642,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50086,-0.00614,0.16202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1238.0,"contact_point_centroid":[0.50656,-0.02269,0.1585],"force_p95":0.12127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17973,"mean_force":0.09129,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50136,-0.0047,0.16317]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01566,-0.00204],"force_p95":0.13366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16571,"mean_force":0.12566,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49217,-0.01528,0.05701]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49888,-0.00701,0.21904]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49796,-0.01479,0.10148]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.51835,0.00249,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57657,0.16971,0.28419]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51835,0.00249,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57835,0.18014,0.25422]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.51835,0.00249,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57981,0.18262,0.30246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3040.0,"contact_point_centroid":[0.49096,0.0035,0.0528],"force_p95":0.09111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10165,"mean_force":0.06762,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49107,-0.01526,0.05579]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2944.0,"contact_point_centroid":[0.49134,-0.03407,0.05246],"force_p95":0.09217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09256,"mean_force":0.0704,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49107,-0.01526,0.05579]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3083.0,"contact_point_centroid":[0.5447,0.09552,0.25752],"force_p95":0.01143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01059,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54463,0.09552,0.2552]},{"body_a":"left_finger","body_b":"right_finger","contact_count":924.0,"contact_point_centroid":[0.57659,0.16979,0.28627],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01293,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57659,0.16977,0.284]}],"total_contact_groups":17},"final_pose_error":0.01352,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51835,0.00249,0.01602],"final_tcp_position":[0.58433,0.18612,0.33491],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273009.00107,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49966,-0.01428,0.13881],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49879,-0.01537,0.0644],"tcp_start":[0.49966,-0.01428,0.13881],"tcp_to_object_dist_end":0.03871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01541,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3122,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13303,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7784.0,"raw_peak_contact_force":0.16571,"subtask_id":"grasp_object","tcp_end":[0.49104,-0.01526,0.05575],"tcp_start":[0.49879,-0.01537,0.0644],"tcp_to_object_dist_end":0.03249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50507,-0.01577,0.11924],"object_pos_start":[0.50375,-0.01541,0.02586],"object_to_goal_dist_end":0.25417,"object_to_goal_dist_start":0.3122,"object_z_max":0.11913,"peak_contact_force":0.11378,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12430.0,"raw_peak_contact_force":0.27507,"subtask_id":"lift_object","tcp_end":[0.49918,-0.01533,0.15662],"tcp_start":[0.49104,-0.01526,0.05575],"tcp_to_object_dist_end":0.03784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51835,0.00249,0.01602],"object_pos_start":[0.50507,-0.01577,0.11924],"object_to_goal_dist_end":0.3046,"object_to_goal_dist_start":0.25417,"object_z_max":0.13108,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8586.0,"raw_peak_contact_force":1.45379,"subtask_id":"reach_goal","tcp_end":[0.57319,0.15992,0.31521],"tcp_start":[0.49918,-0.01533,0.15662],"tcp_to_object_dist_end":0.3425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.51835,0.00249,0.01602],"object_pos_start":[0.51835,0.00249,0.01602],"object_to_goal_dist_end":0.3046,"object_to_goal_dist_start":0.3046,"object_z_max":0.01602,"peak_contact_force":273009.00107,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1796.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.58155,0.18114,0.25337],"tcp_start":[0.57319,0.15992,0.31521],"tcp_to_object_dist_end":0.30372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51835,0.00249,0.01602],"object_pos_start":[0.51835,0.00249,0.01602],"object_to_goal_dist_end":0.3046,"object_to_goal_dist_start":0.3046,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57728,0.17969,0.2741],"tcp_start":[0.58155,0.18114,0.25337],"tcp_to_object_dist_end":0.31856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":600.0,"object_pos_end":[0.51835,0.00249,0.01602],"object_pos_start":[0.51835,0.00249,0.01602],"object_to_goal_dist_end":0.3046,"object_to_goal_dist_start":0.3046,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58433,0.18612,0.33491],"tcp_start":[0.57728,0.17969,0.2741],"tcp_to_object_dist_end":0.37385,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50336,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.move_speed":0.28101,"approach_object.approach_speed":0.33336,"descend_to_grasp.descend_speed":0.05071,"descend_to_place.place_speed":0.04103,"grasp_object.grasp_timeout":0.32269,"lift_object.lift_height":0.05152,"release_object.release_timeout":0.2941},"optimized_scores":{"best_composite_score":-0.19171,"best_fitness_score":0.33829,"best_task_score":0.27388},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2858.0,"contact_point_centroid":[0.5253,0.06982,-0.00213],"force_p95":0.12478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98173,"mean_force":0.1333,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56992,0.11205,0.15971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2348.0,"contact_point_centroid":[0.51091,0.03104,0.07576],"force_p95":0.15494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28647,"mean_force":0.09496,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51366,0.04979,0.08024]},{"body_a":"world","body_b":"grasp_target","contact_count":488.0,"contact_point_centroid":[0.51591,0.03708,-0.00108],"force_p95":0.1373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25552,"mean_force":0.05329,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50023,0.03814,0.0581]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03968,-0.00211],"force_p95":0.15575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20996,"mean_force":0.13089,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50067,0.03825,0.05666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3216.0,"contact_point_centroid":[0.50333,0.05683,0.0592],"force_p95":0.11146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20517,"mean_force":0.08667,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50262,0.03826,0.06255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3073.0,"contact_point_centroid":[0.51353,0.06856,0.07653],"force_p95":0.1065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19629,"mean_force":0.07333,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51408,0.0503,0.08085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3352.0,"contact_point_centroid":[0.5021,0.01975,0.05854],"force_p95":0.1137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18241,"mean_force":0.0823,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50232,0.03825,0.06201]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50279,0.01785,0.21836]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50627,0.03741,0.101]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.52529,0.0694,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61289,0.1602,0.18084]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52529,0.0694,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61535,0.16655,0.14931]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.52529,0.0694,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61706,0.16811,0.19747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2846.0,"contact_point_centroid":[0.49965,0.01949,0.05203],"force_p95":0.09274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11044,"mean_force":0.07142,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49955,0.03816,0.05539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2754.0,"contact_point_centroid":[0.50048,0.05696,0.05198],"force_p95":0.10171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10604,"mean_force":0.07494,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49956,0.03816,0.0554]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2630.0,"contact_point_centroid":[0.5751,0.11757,0.16911],"force_p95":0.01132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01062,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57497,0.11756,0.16683]},{"body_a":"left_finger","body_b":"right_finger","contact_count":935.0,"contact_point_centroid":[0.61288,0.16019,0.18315],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01065,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61287,0.16018,0.18095]}],"total_contact_groups":17},"final_pose_error":0.01482,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.52529,0.0694,0.01602],"final_tcp_position":[0.62342,0.17104,0.23088],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.98173,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50764,0.03626,0.13799],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.50732,0.03878,0.06431],"tcp_start":[0.50764,0.03626,0.13799],"tcp_to_object_dist_end":0.03865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03894,0.02561],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21295,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15181,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7400.0,"raw_peak_contact_force":0.20996,"subtask_id":"grasp_object","tcp_end":[0.49952,0.03816,0.05536],"tcp_start":[0.50732,0.03878,0.06431],"tcp_to_object_dist_end":0.03246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":292.0,"n_steps_budget":600.0,"object_pos_end":[0.51289,0.03879,0.0356],"object_pos_start":[0.51248,0.03894,0.02561],"object_to_goal_dist_end":0.20739,"object_to_goal_dist_start":0.21295,"object_z_max":0.03557,"peak_contact_force":0.10964,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7056.0,"raw_peak_contact_force":0.25552,"subtask_id":"lift_object","tcp_end":[0.50644,0.03848,0.06922],"tcp_start":[0.49952,0.03816,0.05536],"tcp_to_object_dist_end":0.03423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52529,0.0694,0.01602],"object_pos_start":[0.51289,0.03879,0.0356],"object_to_goal_dist_end":0.19426,"object_to_goal_dist_start":0.20739,"object_z_max":0.05887,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10909.0,"raw_peak_contact_force":0.98173,"subtask_id":"reach_goal","tcp_end":[0.60814,0.15376,0.21342],"tcp_start":[0.50644,0.03848,0.06922],"tcp_to_object_dist_end":0.2301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.52529,0.0694,0.01602],"object_pos_start":[0.52529,0.0694,0.01602],"object_to_goal_dist_end":0.19426,"object_to_goal_dist_start":0.19426,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1831.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62001,0.16786,0.14922],"tcp_start":[0.60814,0.15376,0.21342],"tcp_to_object_dist_end":0.19081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52529,0.0694,0.01602],"object_pos_start":[0.52529,0.0694,0.01602],"object_to_goal_dist_end":0.19426,"object_to_goal_dist_start":0.19426,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61364,0.16599,0.16886],"tcp_start":[0.62001,0.16786,0.14922],"tcp_to_object_dist_end":0.20123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.52529,0.0694,0.01602],"object_pos_start":[0.52529,0.0694,0.01602],"object_to_goal_dist_end":0.19426,"object_to_goal_dist_start":0.19426,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62342,0.17104,0.23088],"tcp_start":[0.61364,0.16599,0.16886],"tcp_to_object_dist_end":0.25715,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```