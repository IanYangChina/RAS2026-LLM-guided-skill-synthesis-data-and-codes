## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | descend → grasp → lift → descend → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2419 | 0.29 | ❌ rejected |
| 5 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2314 | 0.24 | ❌ rejected |
| 4 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1488 | 0.19 | ❌ rejected |
| 3 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1969 | 0.28 | ❌ rejected |
| 2 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2195 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.242) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place
  weight: 0.5
phases:
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
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
  guards:
  - id: bilateral_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_1
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_clear
- id: transport_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_2
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.242
- **task_score** (E): 0.285
- **fitness_score**: 0.612  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2585 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.0947 |
| transport_1 | 0.67 | 1.00 | 0.2723 |
| descend_2 | 1.00 | 1.00 | 0.0866 |
| release_1 | 1.00 | 1.00 | 0.0211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.046) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.046)→(0.508, -0.001, 0.037) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 43.667 | 0.170 | 0.252 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.037)→(0.504, -0.001, 0.132) | (0.522, -0.001, 0.025)→(0.519, -0.001, 0.113) | 0.290→0.246 | 1.00 / 28.333 | 0.093 | 0.553 |
| transport_1 | descend | 0.67 / step_budget | (0.504, -0.001, 0.132)→(0.597, 0.186, 0.304) | (0.519, -0.001, 0.113)→(0.599, 0.190, 0.181) | 0.246→0.123 | 1.00 / 10.000 | 3249.725 | 0.876 |
| descend_2 | descend | 1.00 / step_budget | (0.597, 0.186, 0.304)→(0.604, 0.203, 0.221) | (0.599, 0.190, 0.181)→(0.610, 0.195, 0.014) | 0.123→0.192 | 1.00 / 7.000 | 94255.810 | 1.519 |
| release_1 | release | 1.00 / step_budget | (0.604, 0.203, 0.221)→(0.599, 0.201, 0.241) | (0.610, 0.195, 0.014)→(0.610, 0.196, 0.016) | 0.192→0.190 | 1.00 / 4.000 | 0.123 | 0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.341
- phase_score: 0.605
- phase_breakdown.pre_grasp_score: 0.609
- phase_breakdown.lift_clear_score: 0.621
- phase_breakdown.place_score: 0.593
- grasp_place_fitness: 0.634

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.634
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.341
- **Median Q (composite search score)**: 0.231
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.249


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69192,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.0077,"descend_2.place_z_offset":8e-05,"lift_1.lift_height":0.1067,"transport_1.approach_height":0.11416,"transport_1.transport_speed":0.06453},"optimized_scores":{"best_composite_score":0.23061,"best_fitness_score":0.60061,"best_task_score":0.23814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":650.0,"contact_point_centroid":[0.56412,0.22603,-0.00392],"force_p95":0.9427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22006,"mean_force":0.21676,"phase_index":3.0,"phase_name":"transport_1","phase_type":"descend","tcp_position_centroid":[0.56424,0.20317,0.30682]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.47929,0.04306,-0.00144],"force_p95":0.57865,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79148,"mean_force":0.10267,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46963,0.04505,0.02531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10421.0,"contact_point_centroid":[0.46918,0.0637,0.06704],"force_p95":0.09987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32243,"mean_force":0.06111,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46728,0.04483,0.06542]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48286,0.04807,-0.00234],"force_p95":0.22043,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31697,"mean_force":0.1491,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47238,0.04533,0.0242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9463.0,"contact_point_centroid":[0.46933,0.02581,0.069],"force_p95":0.1098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31095,"mean_force":0.06522,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46729,0.04483,0.06694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8424.0,"contact_point_centroid":[0.50647,0.08486,0.18429],"force_p95":0.14145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24435,"mean_force":0.08798,"phase_index":3.0,"phase_name":"transport_1","phase_type":"descend","tcp_position_centroid":[0.50076,0.10281,0.18523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8723.0,"contact_point_centroid":[0.50517,0.12498,0.18962],"force_p95":0.14206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23715,"mean_force":0.08789,"phase_index":3.0,"phase_name":"transport_1","phase_type":"descend","tcp_position_centroid":[0.50293,0.1063,0.18943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4461.0,"contact_point_centroid":[0.47158,0.02594,0.02575],"force_p95":0.08308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14804,"mean_force":0.04784,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47125,0.04522,0.02307]},{"body_a":"world","body_b":"grasp_target","contact_count":3348.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48847,0.02289,0.16395]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.56394,0.22582,-0.00199],"force_p95":0.12277,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1231,"mean_force":0.12261,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57463,0.22066,0.28157]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56394,0.22582,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57461,0.22437,0.24]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5719.0,"contact_point_centroid":[0.47065,0.06477,0.0245],"force_p95":0.07686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08586,"mean_force":0.04164,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47127,0.04523,0.02308]},{"body_a":"left_finger","body_b":"right_finger","contact_count":573.0,"contact_point_centroid":[0.56503,0.20525,0.31172],"force_p95":0.01352,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01095,"phase_index":3.0,"phase_name":"transport_1","phase_type":"descend","tcp_position_centroid":[0.56574,0.20553,0.30968]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1041.0,"contact_point_centroid":[0.57396,0.22036,0.2838],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01025,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57462,0.22065,0.28175]},{"body_a":"left_finger","body_b":"right_finger","contact_count":230.0,"contact_point_centroid":[0.57578,0.22488,0.23741],"force_p95":0.01083,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01085,"mean_force":0.00973,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57645,0.22516,0.23536]}],"total_contact_groups":15},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56394,0.22582,0.01602],"final_tcp_position":[0.57782,0.22565,0.23886],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.93641,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":838.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3348.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47915,0.04592,0.03107],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04535,0.02484],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29295,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20141,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11980.0,"raw_peak_contact_force":0.31697,"tcp_end":[0.47123,0.04522,0.02304],"tcp_start":[0.47915,0.04592,0.03107],"tcp_to_object_dist_end":0.0115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.48527,0.04502,0.111],"object_pos_start":[0.48259,0.04535,0.02484],"object_to_goal_dist_end":0.23959,"object_to_goal_dist_start":0.29295,"object_z_max":0.11089,"peak_contact_force":0.10505,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20034.0,"raw_peak_contact_force":0.79148,"subtask_id":"lift_clear","tcp_end":[0.46725,0.04484,0.11843],"tcp_start":[0.47123,0.04522,0.02304],"tcp_to_object_dist_end":0.0195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56394,0.22583,0.016],"object_pos_start":[0.48527,0.04502,0.111],"object_to_goal_dist_end":0.21525,"object_to_goal_dist_start":0.23959,"object_z_max":0.24605,"peak_contact_force":9748.93641,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18370.0,"raw_peak_contact_force":2.22006,"tcp_end":[0.57272,0.21651,0.32298],"tcp_start":[0.46725,0.04484,0.11843],"tcp_to_object_dist_end":0.30724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.56394,0.22582,0.01602],"object_pos_start":[0.56394,0.22583,0.016],"object_to_goal_dist_end":0.21524,"object_to_goal_dist_start":0.21525,"object_z_max":0.01602,"peak_contact_force":9748.81021,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1997.0,"raw_peak_contact_force":0.1231,"subtask_id":"place","tcp_end":[0.57782,0.22565,0.23886],"tcp_start":[0.57272,0.21651,0.32298],"tcp_to_object_dist_end":0.22327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56394,0.22582,0.01602],"object_pos_start":[0.56394,0.22582,0.01602],"object_to_goal_dist_end":0.21524,"object_to_goal_dist_start":0.21524,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1030.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57353,0.22389,0.26011],"tcp_start":[0.57782,0.22565,0.23886],"tcp_to_object_dist_end":0.24429,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43415,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.01687,"descend_2.place_z_offset":0.00796,"lift_1.lift_height":0.10799,"transport_1.approach_height":0.15611,"transport_1.transport_speed":0.04973},"optimized_scores":{"best_composite_score":0.23135,"best_fitness_score":0.60135,"best_task_score":0.27618},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.62383,0.20715,-0.00374],"force_p95":0.79864,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33504,"mean_force":0.20283,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60039,0.20878,0.2509]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.5344,-0.01979,-0.00121],"force_p95":0.3141,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43681,"mean_force":0.07027,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52054,-0.01999,0.04607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9603.0,"contact_point_centroid":[0.52165,-0.03887,0.08967],"force_p95":0.0985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28857,"mean_force":0.06493,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51803,-0.01993,0.08752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9718.0,"contact_point_centroid":[0.52151,-0.00104,0.08856],"force_p95":0.09622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2864,"mean_force":0.06394,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51803,-0.01993,0.08607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.60439,0.17432,0.31377],"force_p95":0.11377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24475,"mean_force":0.03635,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59284,0.18582,0.31688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9826.0,"contact_point_centroid":[0.55252,0.09068,0.21735],"force_p95":0.14522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23107,"mean_force":0.09163,"phase_index":3.0,"phase_name":"transport_1","phase_type":"descend","tcp_position_centroid":[0.54934,0.07154,0.21655]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02121,-0.00211],"force_p95":0.15298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21363,"mean_force":0.13098,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52338,-0.02004,0.0457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10678.0,"contact_point_centroid":[0.55856,0.05579,0.21808],"force_p95":0.13113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20253,"mean_force":0.0851,"phase_index":3.0,"phase_name":"transport_1","phase_type":"descend","tcp_position_centroid":[0.54988,0.07295,0.21782]},{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5141,-0.01002,0.17567]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62407,0.20701,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60163,0.21984,0.22108]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.52329,-0.00084,0.04709],"force_p95":0.06965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10757,"mean_force":0.04403,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52219,-0.02001,0.0443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.52325,-0.03929,0.04611],"force_p95":0.07219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0739,"mean_force":0.04473,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52219,-0.02001,0.04431]},{"body_a":"left_finger","body_b":"right_finger","contact_count":741.0,"contact_point_centroid":[0.60063,0.21036,0.24862],"force_p95":0.01306,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01073,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60108,0.21056,0.24644]},{"body_a":"left_finger","body_b":"right_finger","contact_count":232.0,"contact_point_centroid":[0.60302,0.22048,0.21915],"force_p95":0.0108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01083,"mean_force":0.00966,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60371,0.22076,0.21703]}],"total_contact_groups":14},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62407,0.20701,0.01602],"final_tcp_position":[0.60517,0.22107,0.2206],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273018.55788,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53047,-0.02013,0.05407],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02046,0.02559],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3163,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14888,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11682.0,"raw_peak_contact_force":0.21363,"tcp_end":[0.52216,-0.02001,0.04427],"tcp_start":[0.53047,-0.02013,0.05407],"tcp_to_object_dist_end":0.02384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53118,-0.01996,0.11497],"object_pos_start":[0.53697,-0.02046,0.02559],"object_to_goal_dist_end":0.27599,"object_to_goal_dist_start":0.3163,"object_z_max":0.11485,"peak_contact_force":0.0865,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19467.0,"raw_peak_contact_force":0.43681,"subtask_id":"lift_clear","tcp_end":[0.51808,-0.01992,0.13983],"tcp_start":[0.52216,-0.02001,0.04427],"tcp_to_object_dist_end":0.0281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60104,0.18678,0.28378],"object_pos_start":[0.53118,-0.01996,0.11497],"object_to_goal_dist_end":0.08716,"object_to_goal_dist_start":0.27599,"object_z_max":0.28404,"peak_contact_force":0.11367,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20504.0,"raw_peak_contact_force":0.23107,"tcp_end":[0.5926,0.18508,0.31775],"tcp_start":[0.51808,-0.01992,0.13983],"tcp_to_object_dist_end":0.03504,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.62408,0.20701,0.01602],"object_pos_start":[0.60104,0.18678,0.28378],"object_to_goal_dist_end":0.193,"object_to_goal_dist_start":0.08716,"object_z_max":0.28378,"peak_contact_force":273018.55788,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1629.0,"raw_peak_contact_force":2.33504,"subtask_id":"place","tcp_end":[0.60517,0.22107,0.2206],"tcp_start":[0.5926,0.18508,0.31775],"tcp_to_object_dist_end":0.20593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62407,0.20701,0.01602],"object_pos_start":[0.62408,0.20701,0.01602],"object_to_goal_dist_end":0.193,"object_to_goal_dist_start":0.193,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.60041,0.21931,0.24082],"tcp_start":[0.60517,0.22107,0.2206],"tcp_to_object_dist_end":0.22638,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40094,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.01704,"descend_2.place_z_offset":0.01751,"lift_1.lift_height":0.10541,"transport_1.approach_height":0.11123,"transport_1.transport_speed":0.04677},"optimized_scores":{"best_composite_score":0.26362,"best_fitness_score":0.63362,"best_task_score":0.34074},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.64052,0.15421,-0.00877],"force_p95":1.55457,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09924,"mean_force":0.44611,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62748,0.16107,0.21075]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.54283,-0.02713,-0.00127],"force_p95":0.28315,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43116,"mean_force":0.07135,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52845,-0.02736,0.04546]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":329.0,"contact_point_centroid":[0.62702,0.17543,0.26327],"force_p95":0.20444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32474,"mean_force":0.16183,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62514,0.15612,0.26439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":530.0,"contact_point_centroid":[0.63622,0.14147,0.25921],"force_p95":0.16036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31955,"mean_force":0.09991,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62512,0.15626,0.26201]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8980.0,"contact_point_centroid":[0.52999,-0.00845,0.08797],"force_p95":0.10416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30629,"mean_force":0.06809,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52599,-0.02728,0.08547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8974.0,"contact_point_centroid":[0.53009,-0.04614,0.08822],"force_p95":0.10374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29396,"mean_force":0.06901,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52598,-0.02728,0.08617]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54567,-0.02908,-0.00216],"force_p95":0.16455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22594,"mean_force":0.13432,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53139,-0.02745,0.0451]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9744.0,"contact_point_centroid":[0.57346,0.07619,0.19773],"force_p95":0.12491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17558,"mean_force":0.08535,"phase_index":3.0,"phase_name":"transport_1","phase_type":"descend","tcp_position_centroid":[0.56993,0.05708,0.19682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9981.0,"contact_point_centroid":[0.57831,0.03947,0.19701],"force_p95":0.12442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16615,"mean_force":0.08417,"phase_index":3.0,"phase_name":"transport_1","phase_type":"descend","tcp_position_centroid":[0.56984,0.05694,0.1967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4772.0,"contact_point_centroid":[0.53125,-0.00821,0.04666],"force_p95":0.07084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14598,"mean_force":0.04488,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53018,-0.02741,0.04366]},{"body_a":"world","body_b":"grasp_target","contact_count":3228.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51819,-0.01377,0.17525]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64117,0.15387,-0.00202],"force_p95":0.12681,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1282,"mean_force":0.1153,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62412,0.161,0.20255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.53142,-0.04672,0.04545],"force_p95":0.07433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07641,"mean_force":0.04463,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53019,-0.02741,0.04367]},{"body_a":"left_finger","body_b":"right_finger","contact_count":184.0,"contact_point_centroid":[0.62552,0.16136,0.20018],"force_p95":0.01438,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01137,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6262,0.16162,0.19801]}],"total_contact_groups":14},"final_pose_error":0.00973,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64117,0.15387,0.01602],"final_tcp_position":[0.62808,0.16203,0.20241],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":2.09924,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":808.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3228.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53855,-0.02762,0.05372],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54558,-0.02785,0.02545],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26024,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15987,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11603.0,"raw_peak_contact_force":0.22594,"tcp_end":[0.53015,-0.02742,0.04362],"tcp_start":[0.53855,-0.02762,0.05372],"tcp_to_object_dist_end":0.02385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53909,-0.02734,0.11183],"object_pos_start":[0.54558,-0.02785,0.02545],"object_to_goal_dist_end":0.2236,"object_to_goal_dist_start":0.26024,"object_z_max":0.11172,"peak_contact_force":0.0865,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18109.0,"raw_peak_contact_force":0.43116,"subtask_id":"lift_clear","tcp_end":[0.52601,-0.02727,0.13659],"tcp_start":[0.53015,-0.02742,0.04362],"tcp_to_object_dist_end":0.02801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.63227,0.15789,0.24195],"object_pos_start":[0.53909,-0.02734,0.11183],"object_to_goal_dist_end":0.06541,"object_to_goal_dist_start":0.2236,"object_z_max":0.24182,"peak_contact_force":0.12473,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19725.0,"raw_peak_contact_force":0.17558,"tcp_end":[0.62522,0.15521,0.27264],"tcp_start":[0.52601,-0.02727,0.13659],"tcp_to_object_dist_end":0.03161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.6422,0.15226,0.01102],"object_pos_start":[0.63227,0.15789,0.24195],"object_to_goal_dist_end":0.16665,"object_to_goal_dist_start":0.06541,"object_z_max":0.24197,"peak_contact_force":0.0613,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1039.0,"raw_peak_contact_force":2.09924,"subtask_id":"place","tcp_end":[0.62808,0.16203,0.20241],"tcp_start":[0.62522,0.15521,0.27264],"tcp_to_object_dist_end":0.19216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64117,0.15387,0.01602],"object_pos_start":[0.6422,0.15226,0.01102],"object_to_goal_dist_end":0.1615,"object_to_goal_dist_start":0.16665,"object_z_max":0.01679,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":984.0,"raw_peak_contact_force":0.1282,"tcp_end":[0.62275,0.16059,0.22223],"tcp_start":[0.62808,0.16203,0.20241],"tcp_to_object_dist_end":0.20714,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```