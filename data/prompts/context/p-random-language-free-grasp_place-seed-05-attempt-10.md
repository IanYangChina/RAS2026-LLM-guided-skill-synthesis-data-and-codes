## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1664 | 0.32 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.3836 | 0.52 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0608 | 0.36 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0416 | 0.32 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0563 | 0.35 | ✅ accepted |

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

## Current Skill (Q=0.166) — your mutation base

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
  - 0.1
  weight: 0.5
- id: reach_goal
  weight: 0.5
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
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_object
- id: descend_to_object
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
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp_object
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
  guards:
  - id: grasp_contact
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_object
  type: lift
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
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_contact, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.166
- **task_score** (E): 0.324
- **fitness_score**: 0.636  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_object | 1.00 | 1.00 | 0.1080 |
| grasp_object | 1.00 | 1.00 | 0.0120 |
| lift_object | 1.00 | 1.00 | 0.0971 |
| transport_carry | 0.00 | 1.00 | 0.0849 |
| descend_to_place | 0.67 | 1.00 | 0.0599 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.510, 0.017, 0.138)→(0.510, 0.018, 0.030) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.030)→(0.502, 0.017, 0.021) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.025) | 0.236→0.237 | 1.00 / 43.000 | 0.159 | 0.226 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.021)→(0.498, 0.017, 0.118) | (0.515, 0.018, 0.025)→(0.513, 0.017, 0.112) | 0.237→0.202 | 1.00 / 35.333 | 524.422 | 0.815 |
| transport_carry | approach | 0.00 / step_budget | (0.498, 0.017, 0.118)→(0.535, 0.078, 0.161) | (0.513, 0.017, 0.112)→(0.545, 0.080, 0.103) | 0.202→0.139 | 1.00 / 22.333 | 91002.354 | 0.558 |
| descend_to_place | descend | 0.67 / step_budget | (0.535, 0.078, 0.161)→(0.566, 0.122, 0.149) | (0.545, 0.080, 0.103)→(0.545, 0.101, 0.016) | 0.139→0.182 | 1.00 / 8.333 | 0.123 | 1.059 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.448
- phase_score: 0.300
- phase_breakdown.reach_goal_score: 0.425
- phase_breakdown.reach_object_score: 0.175
- grasp_place_fitness: 0.698

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.698
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.448
- **Median Q (composite search score)**: 0.186
- **K-run variance**: 0.0036
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.223


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61688,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.07288,"descend_to_object.descend_speed":0.05845,"descend_to_place.descend_place_speed":0.06486,"lift_object.lift_height":0.10539,"lift_object.lift_speed":0.09415,"transport_carry.carry_height":0.09012,"transport_carry.transport_speed":0.07967},"optimized_scores":{"best_composite_score":0.22788,"best_fitness_score":0.69788,"best_task_score":0.4478},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":807.0,"contact_point_centroid":[0.56172,0.11127,-0.00309],"force_p95":0.62257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41574,"mean_force":0.17794,"phase_index":4.0,"phase_name":"transport_carry","phase_type":"approach","tcp_position_centroid":[0.54986,0.09838,0.15378]},{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.52752,0.0288,-0.00122],"force_p95":0.35936,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56391,"mean_force":0.08371,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51442,0.02927,0.03558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9165.0,"contact_point_centroid":[0.51488,0.01027,0.07678],"force_p95":0.10771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31981,"mean_force":0.06985,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51186,0.0291,0.07486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9587.0,"contact_point_centroid":[0.515,0.04791,0.0753],"force_p95":0.10424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31587,"mean_force":0.06783,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5119,0.02911,0.07357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6292.0,"contact_point_centroid":[0.53128,0.03995,0.13458],"force_p95":0.14946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25547,"mean_force":0.10193,"phase_index":4.0,"phase_name":"transport_carry","phase_type":"approach","tcp_position_centroid":[0.52589,0.05827,0.13576]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03054,-0.00212],"force_p95":0.15896,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22789,"mean_force":0.13223,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51736,0.02947,0.03518]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7168.0,"contact_point_centroid":[0.5314,0.07709,0.1344],"force_p95":0.13632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17228,"mean_force":0.0902,"phase_index":4.0,"phase_name":"transport_carry","phase_type":"approach","tcp_position_centroid":[0.52624,0.05889,0.136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.51713,0.01018,0.03654],"force_p95":0.08054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14967,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51614,0.02939,0.0338]},{"body_a":"world","body_b":"grasp_target","contact_count":2204.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51076,0.01382,0.21817]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56185,0.11171,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56424,0.1263,0.13513]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52294,0.02922,0.07534]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.51706,0.04854,0.03559],"force_p95":0.07324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08339,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51615,0.02939,0.0338]},{"body_a":"left_finger","body_b":"right_finger","contact_count":562.0,"contact_point_centroid":[0.55147,0.10056,0.15701],"force_p95":0.01389,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01588,"mean_force":0.01109,"phase_index":4.0,"phase_name":"transport_carry","phase_type":"approach","tcp_position_centroid":[0.55117,0.10055,0.15478]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4234.0,"contact_point_centroid":[0.56472,0.12631,0.13734],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56423,0.12629,0.13514]}],"total_contact_groups":14},"final_pose_error":0.04275,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56185,0.11171,0.01602],"final_tcp_position":[0.57689,0.14617,0.12114],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273006.81448,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2204.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52416,0.02817,0.13727],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52427,0.02992,0.04307],"tcp_start":[0.52416,0.02817,0.13727],"tcp_to_object_dist_end":0.01817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.0295,0.02558],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18463,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15173,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10869.0,"raw_peak_contact_force":0.22789,"tcp_end":[0.51611,0.02938,0.03376],"tcp_start":[0.52427,0.02992,0.04307],"tcp_to_object_dist_end":0.01649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.5263,0.02921,0.11037],"object_pos_start":[0.53042,0.0295,0.02558],"object_to_goal_dist_end":0.16726,"object_to_goal_dist_start":0.18463,"object_z_max":0.11027,"peak_contact_force":0.09897,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18909.0,"raw_peak_contact_force":0.56391,"tcp_end":[0.51194,0.02912,0.1273],"tcp_start":[0.51611,0.02938,0.03376],"tcp_to_object_dist_end":0.02219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56185,0.11171,0.01602],"object_pos_start":[0.5263,0.02921,0.11037],"object_to_goal_dist_end":0.12051,"object_to_goal_dist_start":0.16726,"object_z_max":0.12166,"peak_contact_force":273006.81448,"phase_name":"transport_carry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14829.0,"raw_peak_contact_force":1.41574,"tcp_end":[0.55379,0.10481,0.15674],"tcp_start":[0.51194,0.02912,0.1273],"tcp_to_object_dist_end":0.14112,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56185,0.11171,0.01602],"object_pos_start":[0.56185,0.11171,0.01602],"object_to_goal_dist_end":0.12051,"object_to_goal_dist_start":0.12051,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8234.0,"raw_peak_contact_force":0.12265,"subtask_id":"reach_goal","tcp_end":[0.57689,0.14617,0.12114],"tcp_start":[0.55379,0.10481,0.15674],"tcp_to_object_dist_end":0.11164,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27174,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.07575,"descend_to_object.descend_speed":0.04985,"descend_to_place.descend_place_speed":0.0491,"lift_object.lift_height":0.14622,"lift_object.lift_speed":0.05955,"transport_carry.carry_height":0.12038,"transport_carry.transport_speed":0.06447},"optimized_scores":{"best_composite_score":0.08507,"best_fitness_score":0.55507,"best_task_score":0.15971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2194.0,"contact_point_centroid":[0.51347,0.05925,-0.00246],"force_p95":0.15986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66886,"mean_force":0.14466,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52056,0.06655,0.18429]},{"body_a":"world","body_b":"grasp_target","contact_count":206.0,"contact_point_centroid":[0.49902,-0.01541,-0.00127],"force_p95":0.63595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90638,"mean_force":0.13362,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48885,-0.01544,0.01765]},{"body_a":"grasp_target","body_b":"hand","contact_count":254.0,"contact_point_centroid":[0.50476,-0.02177,0.06581],"force_p95":0.0935,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41674,"mean_force":0.06564,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48686,-0.01541,0.0276]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18672.0,"contact_point_centroid":[0.48666,0.00379,0.06824],"force_p95":0.07847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27335,"mean_force":0.05447,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48641,-0.0154,0.06613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21077.0,"contact_point_centroid":[0.4865,-0.03446,0.06627],"force_p95":0.07342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26559,"mean_force":0.04913,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48643,-0.0154,0.06449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3798.0,"contact_point_centroid":[0.51058,0.02949,0.17352],"force_p95":0.13267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17112,"mean_force":0.09326,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51144,0.04821,0.17652]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50368,-0.01547,-0.00222],"force_p95":0.15464,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16838,"mean_force":0.13791,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49198,-0.01548,0.01693]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49873,-0.00698,0.21945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18829.0,"contact_point_centroid":[0.49741,-0.00625,0.14355],"force_p95":0.08105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1301,"mean_force":0.05489,"phase_index":4.0,"phase_name":"transport_carry","phase_type":"approach","tcp_position_centroid":[0.49671,0.01283,0.14328]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49776,-0.01506,0.06644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4746.0,"contact_point_centroid":[0.51133,0.06678,0.1731],"force_p95":0.10804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12137,"mean_force":0.07593,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51154,0.04845,0.1766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18963.0,"contact_point_centroid":[0.49794,0.03263,0.1444],"force_p95":0.07947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12007,"mean_force":0.05472,"phase_index":4.0,"phase_name":"transport_carry","phase_type":"approach","tcp_position_centroid":[0.49705,0.01356,0.14416]},{"body_a":"grasp_target","body_b":"hand","contact_count":366.0,"contact_point_centroid":[0.50851,-0.01832,0.05461],"force_p95":0.06777,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09112,"mean_force":0.06149,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49106,-0.01547,0.01598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5376.0,"contact_point_centroid":[0.49046,-0.03454,0.01809],"force_p95":0.06365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08353,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49078,-0.01547,0.0157]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4148.0,"contact_point_centroid":[0.49109,0.00381,0.0182],"force_p95":0.07701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07733,"mean_force":0.05138,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49078,-0.01547,0.0157]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2032.0,"contact_point_centroid":[0.5215,0.06763,0.18704],"force_p95":0.01166,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01074,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52113,0.06763,0.1848]}],"total_contact_groups":16},"final_pose_error":0.14081,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51346,0.05919,0.01602],"final_tcp_position":[0.52537,0.07567,0.18856],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49958,-0.0143,0.13874],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49883,-0.01557,0.02404],"tcp_start":[0.49958,-0.0143,0.13874],"tcp_to_object_dist_end":0.00537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50309,-0.01527,0.0253],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31268,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15295,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11690.0,"raw_peak_contact_force":0.16838,"tcp_end":[0.49075,-0.01546,0.01566],"tcp_start":[0.49883,-0.01557,0.02404],"tcp_to_object_dist_end":0.01566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50039,-0.01532,0.11158],"object_pos_start":[0.50309,-0.01527,0.0253],"object_to_goal_dist_end":0.25932,"object_to_goal_dist_start":0.31268,"object_z_max":0.11148,"peak_contact_force":1573.09317,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40209.0,"raw_peak_contact_force":0.90638,"tcp_end":[0.48651,-0.01539,0.1127],"tcp_start":[0.49075,-0.01546,0.01566],"tcp_to_object_dist_end":0.01393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52417,0.04028,0.16219],"object_pos_start":[0.50039,-0.01532,0.11158],"object_to_goal_dist_end":0.1816,"object_to_goal_dist_start":0.25932,"object_z_max":0.16216,"peak_contact_force":0.12839,"phase_name":"transport_carry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37792.0,"raw_peak_contact_force":0.1301,"tcp_end":[0.51048,0.04046,0.17765],"tcp_start":[0.48651,-0.01539,0.1127],"tcp_to_object_dist_end":0.02065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51346,0.05919,0.01602],"object_pos_start":[0.52417,0.04028,0.16219],"object_to_goal_dist_end":0.27516,"object_to_goal_dist_start":0.1816,"object_z_max":0.16219,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12770.0,"raw_peak_contact_force":1.66886,"subtask_id":"reach_goal","tcp_end":[0.52537,0.07567,0.18856],"tcp_start":[0.51048,0.04046,0.17765],"tcp_to_object_dist_end":0.17374,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50955,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.106,"descend_to_object.descend_speed":0.06437,"descend_to_place.descend_place_speed":0.0993,"lift_object.lift_height":0.13625,"lift_object.lift_speed":0.06073,"transport_carry.carry_height":0.07534,"transport_carry.transport_speed":0.06113},"optimized_scores":{"best_composite_score":0.18618,"best_fitness_score":0.65618,"best_task_score":0.36404},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2112.0,"contact_point_centroid":[0.55922,0.13184,-0.00236],"force_p95":0.17621,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38499,"mean_force":0.14167,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58046,0.12983,0.1386]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.5076,0.03856,-0.00135],"force_p95":0.65999,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97618,"mean_force":0.13845,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49728,0.03837,0.01634]},{"body_a":"grasp_target","body_b":"hand","contact_count":644.0,"contact_point_centroid":[0.50486,0.04056,0.08503],"force_p95":0.11768,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42397,"mean_force":0.05566,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49488,0.03818,0.04615]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51232,0.03908,-0.00238],"force_p95":0.1737,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28042,"mean_force":0.15046,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50051,0.03865,0.0154]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17892.0,"contact_point_centroid":[0.49549,0.01907,0.06778],"force_p95":0.07931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27703,"mean_force":0.05677,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49487,0.03818,0.06544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19649.0,"contact_point_centroid":[0.49547,0.05722,0.0647],"force_p95":0.07749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27291,"mean_force":0.05262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49489,0.03818,0.06281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4204.0,"contact_point_centroid":[0.54804,0.08035,0.13843],"force_p95":0.12786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24136,"mean_force":0.09182,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54921,0.0991,0.14122]},{"body_a":"grasp_target","body_b":"hand","contact_count":387.0,"contact_point_centroid":[0.51715,0.04728,0.05374],"force_p95":0.12064,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22399,"mean_force":0.10188,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49973,0.03859,0.01458]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5295.0,"contact_point_centroid":[0.54924,0.11791,0.13776],"force_p95":0.099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14516,"mean_force":0.07304,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54967,0.09958,0.14111]},{"body_a":"world","body_b":"grasp_target","contact_count":2064.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50277,0.01779,0.21862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17287.0,"contact_point_centroid":[0.51783,0.04504,0.12966],"force_p95":0.08612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12868,"mean_force":0.05905,"phase_index":4.0,"phase_name":"transport_carry","phase_type":"approach","tcp_position_centroid":[0.51704,0.06409,0.12969]},{"body_a":"world","body_b":"grasp_target","contact_count":3968.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50619,0.03802,0.06525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18071.0,"contact_point_centroid":[0.51889,0.08384,0.12999],"force_p95":0.08316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11829,"mean_force":0.05719,"phase_index":4.0,"phase_name":"transport_carry","phase_type":"approach","tcp_position_centroid":[0.51776,0.06485,0.13024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5483.0,"contact_point_centroid":[0.49893,0.05776,0.01636],"force_p95":0.0654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0879,"mean_force":0.04193,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03855,0.01412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4223.0,"contact_point_centroid":[0.49858,0.01932,0.01697],"force_p95":0.0774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0778,"mean_force":0.04887,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49929,0.03855,0.01412]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1910.0,"contact_point_centroid":[0.58329,0.13209,0.14088],"force_p95":0.01166,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01563,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58277,0.13207,0.13847]}],"total_contact_groups":16},"final_pose_error":0.04266,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55915,0.13188,0.01602],"final_tcp_position":[0.59593,0.14486,0.13773],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.38499,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50769,0.0363,0.13783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3968.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50742,0.03923,0.02275],"tcp_start":[0.50769,0.0363,0.13783],"tcp_to_object_dist_end":0.00607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51156,0.03845,0.02489],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21417,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.171,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11893.0,"raw_peak_contact_force":0.28042,"tcp_end":[0.49927,0.03854,0.01409],"tcp_start":[0.50742,0.03923,0.02275],"tcp_to_object_dist_end":0.01636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51161,0.03821,0.1135],"object_pos_start":[0.51156,0.03845,0.02489],"object_to_goal_dist_end":0.18022,"object_to_goal_dist_start":0.21417,"object_z_max":0.11339,"peak_contact_force":0.07528,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38401.0,"raw_peak_contact_force":0.97618,"tcp_end":[0.49492,0.03819,0.11449],"tcp_start":[0.49927,0.03854,0.01409],"tcp_to_object_dist_end":0.01672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55042,0.08726,0.13038],"object_pos_start":[0.51161,0.03821,0.1135],"object_to_goal_dist_end":0.11591,"object_to_goal_dist_start":0.18022,"object_z_max":0.13036,"peak_contact_force":0.11764,"phase_name":"transport_carry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35358.0,"raw_peak_contact_force":0.12868,"tcp_end":[0.5401,0.08744,0.14732],"tcp_start":[0.49492,0.03819,0.11449],"tcp_to_object_dist_end":0.01984,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55915,0.13188,0.01602],"object_pos_start":[0.55042,0.08726,0.13038],"object_to_goal_dist_end":0.15158,"object_to_goal_dist_start":0.11591,"object_z_max":0.13038,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13521.0,"raw_peak_contact_force":1.38499,"subtask_id":"reach_goal","tcp_end":[0.59593,0.14486,0.13773],"tcp_start":[0.5401,0.08744,0.14732],"tcp_to_object_dist_end":0.1278,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```