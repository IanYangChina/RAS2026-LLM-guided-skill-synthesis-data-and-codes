## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2195 | 0.23 | ❌ rejected |
| 1 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2558 | 0.29 | ✅ accepted |
| 0 | descend → grasp → approach → descend → release | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.0443 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.220) — your mutation base

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

- **Composite score**: 0.220
- **task_score** (E): 0.232
- **fitness_score**: 0.590  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2621 |
| grasp_1 | 1.00 | 1.00 | 0.0132 |
| lift_1 | 1.00 | 1.00 | 0.1074 |
| transport_1 | 1.00 | 1.00 | 0.2745 |
| descend_2 | 0.00 | 1.00 | 0.0247 |
| release_1 | 1.00 | 1.00 | 0.0224 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.042) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.042)→(0.507, -0.001, 0.033) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 39.000 | 0.203 | 0.282 |
| lift_1 | lift | 1.00 / step_budget | (0.507, -0.001, 0.033)→(0.503, -0.001, 0.140) | (0.522, -0.001, 0.025)→(0.519, -0.001, 0.124) | 0.290→0.241 | 1.00 / 23.667 | 0.110 | 0.591 |
| transport_1 | approach | 1.00 / step_budget | (0.503, -0.001, 0.140)→(0.594, 0.182, 0.321) | (0.519, -0.001, 0.124)→(0.577, 0.120, 0.011) | 0.241→0.224 | 1.00 / 8.333 | 3249.151 | 1.883 |
| descend_2 | descend | 0.00 / step_budget | (0.594, 0.182, 0.321)→(0.600, 0.190, 0.298) | (0.577, 0.120, 0.011)→(0.580, 0.122, 0.014) | 0.224→0.221 | 1.00 / 9.333 | 121.330 | 541.424 |
| release_1 | release | 1.00 / step_budget | (0.600, 0.190, 0.298)→(0.598, 0.189, 0.320) | (0.580, 0.122, 0.014)→(0.581, 0.123, 0.015) | 0.221→0.219 | 1.00 / 4.333 | 0.185 | 29.737 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.236
- phase_score: 0.517
- phase_breakdown.pre_grasp_score: 0.836
- phase_breakdown.lift_clear_score: 0.698
- phase_breakdown.place_score: 0.282
- grasp_place_fitness: 0.599

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.599
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.244
- **Median Q (composite search score)**: 0.221
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.213


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65198,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.01153,"descend_2.place_z_offset":0.01133,"lift_1.lift_height":0.14511,"transport_1.approach_height":0.16679,"transport_1.transport_speed":0.05262},"optimized_scores":{"best_composite_score":0.22944,"best_fitness_score":0.59944,"best_task_score":0.23567},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":448.0,"contact_point_centroid":[0.56952,0.21557,-0.00057],"force_p95":626.12845,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1624.27252,"mean_force":443.94325,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57064,0.23218,0.28905]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.58652,0.22298,-0.00016],"force_p95":84.87873,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.96689,"mean_force":60.39748,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58578,0.22897,0.2941]},{"body_a":"grasp_target","body_b":"link6","contact_count":580.0,"contact_point_centroid":[0.56604,0.21239,0.01554],"force_p95":1.54222,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.357,"mean_force":1.06364,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56235,0.23701,0.28917]},{"body_a":"world","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.57901,0.21845,-0.00492],"force_p95":0.57054,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.04191,"mean_force":0.33508,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55408,0.23815,0.28647]},{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.57345,0.21248,-0.01411],"force_p95":1.95823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.47811,"mean_force":0.7882,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56561,0.2037,0.35819]},{"body_a":"grasp_target","body_b":"link6","contact_count":200.0,"contact_point_centroid":[0.58964,0.22266,0.01798],"force_p95":0.89137,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.8915,"mean_force":0.71797,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58584,0.22886,0.30035]},{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.47958,0.04204,-0.00171],"force_p95":0.56404,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74492,"mean_force":0.13084,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47067,0.04344,0.03112]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58502,0.22304,-0.00499],"force_p95":0.39205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3998,"mean_force":0.29835,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58584,0.22886,0.30035]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9961.0,"contact_point_centroid":[0.4698,0.06224,0.08849],"force_p95":0.10287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33824,"mean_force":0.06269,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4683,0.04323,0.08663]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4829,0.04802,-0.00247],"force_p95":0.28339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33504,"mean_force":0.1899,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47321,0.0437,0.02991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9424.0,"contact_point_centroid":[0.47048,0.02429,0.09142],"force_p95":0.10341,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30503,"mean_force":0.06371,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46832,0.04323,0.08941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9502.0,"contact_point_centroid":[0.50906,0.08764,0.23393],"force_p95":0.13139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25457,"mean_force":0.08319,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50455,0.10605,0.23506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9427.0,"contact_point_centroid":[0.51132,0.12892,0.23928],"force_p95":0.12896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17042,"mean_force":0.08394,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50731,0.11049,0.24065]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4608.0,"contact_point_centroid":[0.47234,0.02436,0.03084],"force_p95":0.09596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16784,"mean_force":0.05211,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47211,0.04359,0.0288]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48956,0.02174,0.16906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5279.0,"contact_point_centroid":[0.47223,0.06337,0.03054],"force_p95":0.09475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11004,"mean_force":0.0541,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47213,0.0436,0.02882]}],"total_contact_groups":19},"final_pose_error":0.05204,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58851,0.22458,0.01383],"final_tcp_position":[0.58568,0.22932,0.29371],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9747.20743,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48037,0.04424,0.03739],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.04432,0.02439],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29389,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.26467,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11687.0,"raw_peak_contact_force":0.33504,"tcp_end":[0.47208,0.04359,0.02878],"tcp_start":[0.48037,0.04424,0.03739],"tcp_to_object_dist_end":0.01146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":585.0,"n_steps_budget":930.0,"object_pos_end":[0.48555,0.04373,0.14835],"object_pos_start":[0.48265,0.04432,0.02439],"object_to_goal_dist_end":0.22426,"object_to_goal_dist_start":0.29389,"object_z_max":0.14819,"peak_contact_force":0.11225,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19496.0,"raw_peak_contact_force":0.74492,"subtask_id":"lift_clear","tcp_end":[0.46844,0.04325,0.1595],"tcp_start":[0.47208,0.04359,0.02878],"tcp_to_object_dist_end":0.02042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57496,0.21468,0.00083],"object_pos_start":[0.48555,0.04373,0.14835],"object_to_goal_dist_end":0.2302,"object_to_goal_dist_start":0.22426,"object_z_max":0.30356,"peak_contact_force":9747.20743,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19132.0,"raw_peak_contact_force":2.47811,"tcp_end":[0.56738,0.20651,0.36173],"tcp_start":[0.46844,0.04325,0.1595],"tcp_to_object_dist_end":0.36108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":682.0,"n_steps_budget":1000.0,"object_pos_end":[0.58525,0.22313,0.00868],"object_pos_start":[0.57496,0.21468,0.00083],"object_to_goal_dist_end":0.2219,"object_to_goal_dist_start":0.2302,"object_z_max":0.01722,"peak_contact_force":363.74551,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6614.0,"raw_peak_contact_force":1624.27252,"subtask_id":"place","tcp_end":[0.58568,0.22932,0.29371],"tcp_start":[0.56738,0.20651,0.36173],"tcp_to_object_dist_end":0.28509,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58851,0.22458,0.01383],"object_pos_start":[0.58525,0.22313,0.00868],"object_to_goal_dist_end":0.2168,"object_to_goal_dist_start":0.2219,"object_z_max":0.01378,"peak_contact_force":0.31116,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1305.0,"raw_peak_contact_force":88.96689,"tcp_end":[0.58603,0.22879,0.32029],"tcp_start":[0.58568,0.22932,0.29371],"tcp_to_object_dist_end":0.3065,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.09479,"average_mean_iterations":22.01422,"average_solve_count":211.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00264,"descend_2.place_z_offset":0.0014,"lift_1.lift_height":0.10996,"transport_1.approach_height":0.11443,"transport_1.transport_speed":0.05008},"optimized_scores":{"best_composite_score":0.20783,"best_fitness_score":0.57783,"best_task_score":0.21606},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1602.0,"contact_point_centroid":[0.57946,0.10424,-0.00271],"force_p95":0.31387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59844,"mean_force":0.1514,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58064,0.15565,0.25888]},{"body_a":"world","body_b":"grasp_target","contact_count":105.0,"contact_point_centroid":[0.53471,-0.01801,-0.00137],"force_p95":0.42704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50434,"mean_force":0.08601,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51927,-0.01927,0.03689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52126,-0.00043,0.08158],"force_p95":0.11855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4097,"mean_force":0.08876,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51669,-0.01921,0.07916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6245.0,"contact_point_centroid":[0.52124,-0.03771,0.08127],"force_p95":0.11053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36081,"mean_force":0.07898,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51669,-0.01921,0.0796]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53715,-0.02106,-0.00219],"force_p95":0.17462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24718,"mean_force":0.13691,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52192,-0.01931,0.03644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4150.0,"contact_point_centroid":[0.53988,0.05398,0.16614],"force_p95":0.15712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23435,"mean_force":0.10895,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53432,0.03571,0.16777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4709.0,"contact_point_centroid":[0.53955,0.01644,0.16503],"force_p95":0.14045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17784,"mean_force":0.09862,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53391,0.03449,0.16692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4161.0,"contact_point_centroid":[0.5224,-0.00025,0.03741],"force_p95":0.09915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15129,"mean_force":0.05484,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52073,-0.01929,0.03509]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5138,-0.00949,0.17344]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57947,0.1043,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59424,0.19598,0.29084]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4631.0,"contact_point_centroid":[0.5227,-0.03829,0.03732],"force_p95":0.08371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08885,"mean_force":0.04905,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52074,-0.01929,0.0351]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1487.0,"contact_point_centroid":[0.58301,0.16089,0.26505],"force_p95":0.01187,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01064,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58269,0.16089,0.26287]},{"body_a":"left_finger","body_b":"right_finger","contact_count":215.0,"contact_point_centroid":[0.59618,0.1968,0.28941],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01032,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59579,0.19679,0.2873]}],"total_contact_groups":13},"final_pose_error":0.08806,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57947,0.1043,0.01602],"final_tcp_position":[0.59671,0.19665,0.29007],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.59844,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52953,-0.01937,0.04546],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53736,-0.01959,0.0253],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3157,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.16595,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10592.0,"raw_peak_contact_force":0.24718,"tcp_end":[0.5207,-0.01929,0.03506],"tcp_start":[0.52953,-0.01937,0.04546],"tcp_to_object_dist_end":0.01931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":470.0,"n_steps_budget":690.0,"object_pos_end":[0.53241,-0.01921,0.11271],"object_pos_start":[0.53736,-0.01959,0.0253],"object_to_goal_dist_end":0.27573,"object_to_goal_dist_start":0.3157,"object_z_max":0.11256,"peak_contact_force":0.11103,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11686.0,"raw_peak_contact_force":0.50434,"subtask_id":"lift_clear","tcp_end":[0.51658,-0.0192,0.13064],"tcp_start":[0.5207,-0.01929,0.03506],"tcp_to_object_dist_end":0.02392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57947,0.1043,0.01602],"object_pos_start":[0.53241,-0.01921,0.11271],"object_to_goal_dist_end":0.22983,"object_to_goal_dist_start":0.27573,"object_z_max":0.18452,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11948.0,"raw_peak_contact_force":1.59844,"tcp_end":[0.59671,0.19665,0.29007],"tcp_start":[0.51658,-0.0192,0.13064],"tcp_to_object_dist_end":0.28971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.57947,0.1043,0.01602],"object_pos_start":[0.57947,0.1043,0.01602],"object_to_goal_dist_end":0.22983,"object_to_goal_dist_start":0.22983,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.59671,0.19665,0.29007],"tcp_start":[0.59671,0.19665,0.29007],"tcp_to_object_dist_end":0.28971,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57947,0.1043,0.01602],"object_pos_start":[0.57947,0.1043,0.01602],"object_to_goal_dist_end":0.22983,"object_to_goal_dist_start":0.22983,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59345,0.19556,0.31034],"tcp_start":[0.59671,0.19665,0.29007],"tcp_to_object_dist_end":0.30846,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":27.0,"average_failure_rate":0.12273,"average_mean_iterations":27.50909,"average_solve_count":220.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00315,"descend_2.place_z_offset":0.01124,"lift_1.lift_height":0.11009,"transport_1.approach_height":0.16603,"transport_1.transport_speed":0.04229},"optimized_scores":{"best_composite_score":0.22129,"best_fitness_score":0.59129,"best_task_score":0.24361},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2387.0,"contact_point_centroid":[0.57525,0.03971,-0.00242],"force_p95":0.13519,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57148,"mean_force":0.14088,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59055,0.09476,0.25745]},{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.54315,-0.02526,-0.00142],"force_p95":0.38858,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52405,"mean_force":0.09112,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52683,-0.02638,0.03569]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5741.0,"contact_point_centroid":[0.52925,-0.00766,0.08259],"force_p95":0.11732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40127,"mean_force":0.08556,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52418,-0.02629,0.08053]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5812.0,"contact_point_centroid":[0.52925,-0.04488,0.08102],"force_p95":0.11449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39832,"mean_force":0.08647,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52418,-0.02629,0.07922]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54572,-0.02889,-0.00226],"force_p95":0.19254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26457,"mean_force":0.1414,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52953,-0.02646,0.03515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2296.0,"contact_point_centroid":[0.54249,0.01955,0.1528],"force_p95":0.17705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2283,"mean_force":0.12214,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53686,0.00138,0.15536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2791.0,"contact_point_centroid":[0.54178,-0.01759,0.15172],"force_p95":0.14876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18645,"mean_force":0.10518,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53631,0.00028,0.15429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3801.0,"contact_point_centroid":[0.53071,-0.00747,0.03716],"force_p95":0.10376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15204,"mean_force":0.05579,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52833,-0.02642,0.03376]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51764,-0.01303,0.17288]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57528,0.03976,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61659,0.14248,0.31104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4085.0,"contact_point_centroid":[0.53132,-0.04553,0.03614],"force_p95":0.09977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10401,"mean_force":0.05543,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52834,-0.02642,0.03377]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2309.0,"contact_point_centroid":[0.59355,0.0994,0.26486],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01054,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59326,0.0994,0.26257]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.61826,0.14308,0.30999],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00992,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.618,0.14307,0.30772]}],"total_contact_groups":13},"final_pose_error":0.12507,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.57528,0.03976,0.01602],"final_tcp_position":[0.61877,0.1429,0.31047],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.57148,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53733,-0.02659,0.04441],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54582,-0.02692,0.02511],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25967,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17771,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9686.0,"raw_peak_contact_force":0.26457,"tcp_end":[0.5283,-0.02642,0.03372],"tcp_start":[0.53733,-0.02659,0.04441],"tcp_to_object_dist_end":0.01953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":483.0,"n_steps_budget":720.0,"object_pos_end":[0.54045,-0.02656,0.11174],"object_pos_start":[0.54582,-0.02692,0.02511],"object_to_goal_dist_end":0.22238,"object_to_goal_dist_start":0.25967,"object_z_max":0.11159,"peak_contact_force":0.1056,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11667.0,"raw_peak_contact_force":0.52405,"subtask_id":"lift_clear","tcp_end":[0.52413,-0.02628,0.12949],"tcp_start":[0.5283,-0.02642,0.03372],"tcp_to_object_dist_end":0.02412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57528,0.03976,0.01602],"object_pos_start":[0.54045,-0.02656,0.11174],"object_to_goal_dist_end":0.21183,"object_to_goal_dist_start":0.22238,"object_z_max":0.16032,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9783.0,"raw_peak_contact_force":1.57148,"tcp_end":[0.61877,0.1429,0.31047],"tcp_start":[0.52413,-0.02628,0.12949],"tcp_to_object_dist_end":0.31501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.57528,0.03976,0.01602],"object_pos_start":[0.57528,0.03976,0.01602],"object_to_goal_dist_end":0.21183,"object_to_goal_dist_start":0.21183,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.61877,0.1429,0.31047],"tcp_start":[0.61877,0.1429,0.31047],"tcp_to_object_dist_end":0.31501,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57528,0.03976,0.01602],"object_pos_start":[0.57528,0.03976,0.01602],"object_to_goal_dist_end":0.21183,"object_to_goal_dist_start":0.21183,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61591,0.14218,0.33042],"tcp_start":[0.61877,0.1429,0.31047],"tcp_to_object_dist_end":0.33316,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```