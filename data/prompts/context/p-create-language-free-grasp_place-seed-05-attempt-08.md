## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2054 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2586 | 0.44 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1986 | 0.31 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2030 | 0.31 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.0961 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.205) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: reach_place
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_1
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
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
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_place
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_depth:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_place
- id: release_1
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
- id: retract_1
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.01
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_depth: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.205
- **task_score** (E): 0.323
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1289 |
| descend_1 | 1.00 | 1.00 | 0.1314 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1030 |
| transport_1 | 0.00 | 1.00 | 0.0757 |
| descend_place | 0.67 | 1.00 | 0.0809 |
| release_1 | 1.00 | 1.00 | 0.0222 |
| retract_1 | 1.00 | 1.00 | 0.0859 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.176) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.016, 0.176)→(0.511, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.045)→(0.503, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.139 | 0.191 |
| lift_1 | lift | 1.00 / step_budget | (0.503, 0.018, 0.036)→(0.511, 0.018, 0.139) | (0.516, 0.018, 0.026)→(0.525, 0.018, 0.120) | 0.237→0.193 | 1.00 / 23.333 | 0.108 | 0.506 |
| transport_1 | approach | 0.00 / step_budget | (0.511, 0.018, 0.139)→(0.542, 0.077, 0.170) | (0.525, 0.018, 0.120)→(0.554, 0.077, 0.011) | 0.193→0.195 | 1.00 / 4.333 | 0.471 | 1.492 |
| descend_place | descend | 0.67 / step_budget | (0.542, 0.077, 0.170)→(0.580, 0.141, 0.182) | (0.554, 0.077, 0.011)→(0.556, 0.085, 0.016) | 0.195→0.186 | 1.00 / 8.667 | 91002.162 | 0.488 |
| release_1 | release | 1.00 / step_budget | (0.580, 0.141, 0.182)→(0.575, 0.140, 0.204) | (0.556, 0.085, 0.016)→(0.556, 0.085, 0.016) | 0.186→0.186 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.575, 0.140, 0.204)→(0.572, 0.139, 0.289) | (0.556, 0.085, 0.016)→(0.556, 0.085, 0.016) | 0.186→0.186 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.468
- phase_score: 0.535
- phase_breakdown.reach_grasp_score: 0.772
- phase_breakdown.reach_place_score: 0.434
- grasp_place_fitness: 0.705

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.705
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.468
- **Median Q (composite search score)**: 0.221
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.430


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64557,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14745,"descend_1.descend_depth":0.02516,"descend_place.place_depth":0.04885,"lift_1.lift_height":0.11891,"transport_1.transport_speed":0.04452},"optimized_scores":{"best_composite_score":0.27477,"best_fitness_score":0.70477,"best_task_score":0.4675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":21.0,"contact_point_centroid":[0.56638,0.10292,-0.00587],"force_p95":1.37779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37864,"mean_force":1.16287,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55538,0.09555,0.15033]},{"body_a":"world","body_b":"grasp_target","contact_count":3992.0,"contact_point_centroid":[0.57519,0.11666,-0.00217],"force_p95":0.12467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99528,"mean_force":0.12806,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57296,0.13331,0.14638]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.52905,0.02964,-0.00117],"force_p95":0.31578,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47114,"mean_force":0.05715,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51609,0.02974,0.04056]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9354.0,"contact_point_centroid":[0.5215,0.01076,0.08201],"force_p95":0.10088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28959,"mean_force":0.06535,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51887,0.02959,0.08027]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9532.0,"contact_point_centroid":[0.52098,0.04852,0.0801],"force_p95":0.10415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28866,"mean_force":0.0648,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51866,0.0296,0.07831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8987.0,"contact_point_centroid":[0.54328,0.04227,0.13836],"force_p95":0.14949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27106,"mean_force":0.0922,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53767,0.06071,0.13808]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03061,-0.00208],"force_p95":0.14625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20447,"mean_force":0.12902,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51854,0.02993,0.04015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9490.0,"contact_point_centroid":[0.54407,0.08047,0.13857],"force_p95":0.12958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17874,"mean_force":0.08705,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53837,0.06214,0.13854]},{"body_a":"world","body_b":"grasp_target","contact_count":1592.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13465,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51077,0.01339,0.24166]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.51788,0.01065,0.04155],"force_p95":0.07875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13746,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51732,0.02985,0.03876]},{"body_a":"world","body_b":"grasp_target","contact_count":3380.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52349,0.02908,0.10404]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57519,0.11664,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58865,0.16827,0.14934]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.57519,0.11664,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58389,0.16674,0.20975]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4944.0,"contact_point_centroid":[0.51789,0.04896,0.04057],"force_p95":0.0713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07825,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51733,0.02985,0.03876]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3998.0,"contact_point_centroid":[0.57472,0.13575,0.14855],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57418,0.13573,0.14629]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.59214,0.16926,0.14751],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.0103,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59158,0.16924,0.14547]}],"total_contact_groups":16},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57519,0.11664,0.01602],"final_tcp_position":[0.58412,0.16677,0.25442],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.37864,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1592.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52393,0.02747,0.1839],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3380.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52541,0.03039,0.04809],"tcp_start":[0.52393,0.02747,0.1839],"tcp_to_object_dist_end":0.02265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.02991,0.02571],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18424,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14172,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10837.0,"raw_peak_contact_force":0.20447,"tcp_end":[0.5173,0.02985,0.03873],"tcp_start":[0.52541,0.03039,0.04809],"tcp_to_object_dist_end":0.01848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53903,0.02974,0.11207],"object_pos_start":[0.53042,0.02991,0.02571],"object_to_goal_dist_end":0.16148,"object_to_goal_dist_start":0.18424,"object_z_max":0.11197,"peak_contact_force":0.0985,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19038.0,"raw_peak_contact_force":0.47114,"tcp_end":[0.52545,0.02963,0.13216],"tcp_start":[0.5173,0.02985,0.03873],"tcp_to_object_dist_end":0.02424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57183,0.1084,0.00745],"object_pos_start":[0.53903,0.02974,0.11207],"object_to_goal_dist_end":0.12624,"object_to_goal_dist_start":0.16148,"object_z_max":0.11899,"peak_contact_force":1.02731,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18498.0,"raw_peak_contact_force":1.37864,"subtask_id":"reach_place","tcp_end":[0.55558,0.09592,0.15046],"tcp_start":[0.52545,0.02963,0.13216],"tcp_to_object_dist_end":0.14448,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57519,0.11664,0.01602],"object_pos_start":[0.57183,0.1084,0.00745],"object_to_goal_dist_end":0.11405,"object_to_goal_dist_start":0.12624,"object_z_max":0.01662,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7990.0,"raw_peak_contact_force":0.99528,"subtask_id":"reach_place","tcp_end":[0.59304,0.16951,0.14823],"tcp_start":[0.55558,0.09592,0.15046],"tcp_to_object_dist_end":0.14351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57519,0.11664,0.01602],"object_pos_start":[0.57519,0.11664,0.01602],"object_to_goal_dist_end":0.11405,"object_to_goal_dist_start":0.11405,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58693,0.1677,0.16908],"tcp_start":[0.59304,0.16951,0.14823],"tcp_to_object_dist_end":0.16178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.57519,0.11664,0.01602],"object_pos_start":[0.57519,0.11664,0.01602],"object_to_goal_dist_end":0.11405,"object_to_goal_dist_start":0.11405,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58412,0.16677,0.25442],"tcp_start":[0.58693,0.1677,0.16908],"tcp_to_object_dist_end":0.24378,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67925,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1056,"descend_1.descend_depth":0.01589,"descend_place.place_depth":0.0744,"lift_1.lift_height":0.13402,"transport_1.transport_speed":0.05728},"optimized_scores":{"best_composite_score":0.12019,"best_fitness_score":0.55019,"best_task_score":0.14528},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.52607,0.02568,-0.00268],"force_p95":0.34654,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60288,"mean_force":0.1557,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51855,0.03783,0.18928]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.502,-0.01535,-0.00108],"force_p95":0.37709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55516,"mean_force":0.0577,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48971,-0.01543,0.0336]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10827.0,"contact_point_centroid":[0.49493,0.00356,0.08442],"force_p95":0.10649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30858,"mean_force":0.06763,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49233,-0.01533,0.08251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11325.0,"contact_point_centroid":[0.49503,-0.03416,0.08357],"force_p95":0.10202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28379,"mean_force":0.06527,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4923,-0.01533,0.082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5378.0,"contact_point_centroid":[0.50887,0.02324,0.15847],"force_p95":0.14651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25964,"mean_force":0.09681,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50436,0.00496,0.16073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5712.0,"contact_point_centroid":[0.50915,-0.01334,0.15835],"force_p95":0.13009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17757,"mean_force":0.09117,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50436,0.00486,0.16071]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01555,-0.00203],"force_p95":0.13095,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15248,"mean_force":0.12509,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49208,-0.01547,0.03307]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49891,-0.00695,0.22238]},{"body_a":"world","body_b":"grasp_target","contact_count":2404.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49781,-0.01491,0.08756]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52613,0.02569,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5337,0.07785,0.21914]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52613,0.02569,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54413,0.10648,0.24709]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.52613,0.02569,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54085,0.10574,0.30923]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.49135,0.00375,0.0346],"force_p95":0.07599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11614,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49091,-0.01545,0.03183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4882.0,"contact_point_centroid":[0.49142,-0.03453,0.03367],"force_p95":0.06811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08851,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49091,-0.01545,0.03183]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1214.0,"contact_point_centroid":[0.51958,0.03963,0.19308],"force_p95":0.01231,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01597,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51934,0.03963,0.19087]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4289.0,"contact_point_centroid":[0.53413,0.07785,0.22148],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5337,0.07784,0.21913]}],"total_contact_groups":17},"final_pose_error":0.01331,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52613,0.02569,0.01602],"final_tcp_position":[0.54118,0.10577,0.35424],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.60288,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49976,-0.01424,0.14458],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2404.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.4988,-0.01556,0.04023],"tcp_start":[0.49976,-0.01424,0.14458],"tcp_to_object_dist_end":0.01507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01531,0.02589],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31213,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12906,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15248,"tcp_end":[0.49088,-0.01545,0.0318],"tcp_start":[0.4988,-0.01556,0.04023],"tcp_to_object_dist_end":0.01411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.5145,-0.01527,0.13214],"object_pos_start":[0.50369,-0.01531,0.02589],"object_to_goal_dist_end":0.24452,"object_to_goal_dist_start":0.31213,"object_z_max":0.13203,"peak_contact_force":0.11247,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22288.0,"raw_peak_contact_force":0.55516,"tcp_end":[0.4991,-0.01525,0.14781],"tcp_start":[0.49088,-0.01545,0.0318],"tcp_to_object_dist_end":0.02197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52613,0.02569,0.01602],"object_pos_start":[0.5145,-0.01527,0.13214],"object_to_goal_dist_end":0.28936,"object_to_goal_dist_start":0.24452,"object_z_max":0.15102,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13688.0,"raw_peak_contact_force":1.60288,"subtask_id":"reach_place","tcp_end":[0.52287,0.04757,0.19789],"tcp_start":[0.4991,-0.01525,0.14781],"tcp_to_object_dist_end":0.18321,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52613,0.02569,0.01602],"object_pos_start":[0.52613,0.02569,0.01602],"object_to_goal_dist_end":0.28936,"object_to_goal_dist_start":0.28936,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8289.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.54727,0.10709,0.2446],"tcp_start":[0.52287,0.04757,0.19789],"tcp_to_object_dist_end":0.24356,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52613,0.02569,0.01602],"object_pos_start":[0.52613,0.02569,0.01602],"object_to_goal_dist_end":0.28936,"object_to_goal_dist_start":0.28936,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54296,0.1062,0.26742],"tcp_start":[0.54727,0.10709,0.2446],"tcp_to_object_dist_end":0.26452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.52613,0.02569,0.01602],"object_pos_start":[0.52613,0.02569,0.01602],"object_to_goal_dist_end":0.28936,"object_to_goal_dist_start":0.28936,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54118,0.10577,0.35424],"tcp_start":[0.54296,0.1062,0.26742],"tcp_to_object_dist_end":0.3479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6131,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16259,"descend_1.descend_depth":0.02179,"descend_place.place_depth":0.01687,"lift_1.lift_height":0.1224,"transport_1.transport_speed":0.01053},"optimized_scores":{"best_composite_score":0.22123,"best_fitness_score":0.65123,"best_task_score":0.35694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.562,0.09639,-0.01107],"force_p95":1.33996,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49394,"mean_force":0.7498,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54686,0.08603,0.1614]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.51091,0.03808,-0.00117],"force_p95":0.33003,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49044,"mean_force":0.05613,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49838,0.03841,0.03912]},{"body_a":"world","body_b":"grasp_target","contact_count":3796.0,"contact_point_centroid":[0.5661,0.11256,-0.00212],"force_p95":0.17429,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3459,"mean_force":0.12771,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57436,0.11888,0.15475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10087.0,"contact_point_centroid":[0.50316,0.0572,0.081],"force_p95":0.10417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29331,"mean_force":0.06439,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50091,0.03825,0.07917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9954.0,"contact_point_centroid":[0.50372,0.01942,0.08325],"force_p95":0.10005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29211,"mean_force":0.06452,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50116,0.03825,0.08149]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8266.0,"contact_point_centroid":[0.5293,0.04177,0.145],"force_p95":0.15094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23023,"mean_force":0.09561,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52376,0.06014,0.14509]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03952,-0.0021],"force_p95":0.15219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21678,"mean_force":0.13051,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50077,0.03864,0.03854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8698.0,"contact_point_centroid":[0.53025,0.07941,0.14523],"force_p95":0.13194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16595,"mean_force":0.09094,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52463,0.06114,0.14569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4084.0,"contact_point_centroid":[0.50006,0.01934,0.04006],"force_p95":0.07973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14129,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49959,0.03855,0.03725]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50287,0.01679,0.24989]},{"body_a":"world","body_b":"grasp_target","contact_count":3320.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50627,0.03701,0.11653]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56628,0.11353,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59639,0.14607,0.15479]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.56628,0.11353,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59166,0.14474,0.21512]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4965.0,"contact_point_centroid":[0.50008,0.05767,0.03906],"force_p95":0.07241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07962,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4996,0.03855,0.03726]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4130.0,"contact_point_centroid":[0.57437,0.11839,0.15701],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57387,0.11837,0.15475]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.59953,0.14693,0.15309],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59931,0.14691,0.15096]}],"total_contact_groups":16},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.56628,0.11353,0.01602],"final_tcp_position":[0.59191,0.14477,0.25979],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273006.23978,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50772,0.03473,0.19979],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50751,0.0392,0.04599],"tcp_start":[0.50772,0.03473,0.19979],"tcp_to_object_dist_end":0.0206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03865,0.02565],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21314,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14641,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10849.0,"raw_peak_contact_force":0.21678,"tcp_end":[0.49957,0.03854,0.03722],"tcp_start":[0.50751,0.0392,0.04599],"tcp_to_object_dist_end":0.0173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52152,0.03849,0.11695],"object_pos_start":[0.51243,0.03865,0.02565],"object_to_goal_dist_end":0.1732,"object_to_goal_dist_start":0.21314,"object_z_max":0.11684,"peak_contact_force":0.11348,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20190.0,"raw_peak_contact_force":0.49044,"tcp_end":[0.50763,0.03832,0.13594],"tcp_start":[0.49957,0.03854,0.03722],"tcp_to_object_dist_end":0.02353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56394,0.09687,0.00924],"object_pos_start":[0.52152,0.03849,0.11695],"object_to_goal_dist_end":0.16796,"object_to_goal_dist_start":0.1732,"object_z_max":0.12972,"peak_contact_force":0.26223,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17050.0,"raw_peak_contact_force":1.49394,"subtask_id":"reach_place","tcp_end":[0.54765,0.0869,0.16196],"tcp_start":[0.50763,0.03832,0.13594],"tcp_to_object_dist_end":0.15391,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56628,0.11353,0.01602],"object_pos_start":[0.56394,0.09687,0.00924],"object_to_goal_dist_end":0.15453,"object_to_goal_dist_start":0.16796,"object_z_max":0.02226,"peak_contact_force":273006.23978,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7926.0,"raw_peak_contact_force":0.3459,"subtask_id":"reach_place","tcp_end":[0.60075,0.14717,0.15375],"tcp_start":[0.54765,0.0869,0.16196],"tcp_to_object_dist_end":0.14591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56628,0.11353,0.01602],"object_pos_start":[0.56628,0.11353,0.01602],"object_to_goal_dist_end":0.15453,"object_to_goal_dist_start":0.15453,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59468,0.14558,0.1745],"tcp_start":[0.60075,0.14717,0.15375],"tcp_to_object_dist_end":0.16416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.56628,0.11353,0.01602],"object_pos_start":[0.56628,0.11353,0.01602],"object_to_goal_dist_end":0.15453,"object_to_goal_dist_start":0.15453,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59191,0.14477,0.25979],"tcp_start":[0.59468,0.14558,0.1745],"tcp_to_object_dist_end":0.24709,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```