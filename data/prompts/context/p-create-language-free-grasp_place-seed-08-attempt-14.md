## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5201 | 0.76 | ❌ rejected |
| 13 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1799 | 0.19 | ❌ rejected |
| 12 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2474 | 0.32 | ❌ rejected |
| 11 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3875 | 0.52 | ❌ rejected |
| 10 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3133 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.520) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place
  offset:
  - 0.0
  - 0.0
  - 0.03
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
    threshold: 0.1
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
  control: impedance_control
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
  guards:
  - id: grasp_retained
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
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
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place

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
    - id=bilateral_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
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
  - guards:
    - id=grasp_retained, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.520
- **task_score** (E): 0.760
- **fitness_score**: 0.860  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2678 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.0998 |
| transport_1 | 1.00 | 1.00 | 0.2728 |
| descend_2 | 1.00 | 1.00 | 0.0774 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.037) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.511, -0.001, 0.031)→(0.511, -0.001, 0.031) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.333 | 0.166 | 0.250 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.031)→(0.507, -0.001, 0.131) | (0.522, -0.001, 0.025)→(0.522, -0.001, 0.118) | 0.290→0.243 | 1.00 / 26.000 | 0.105 | 0.647 |
| transport_1 | approach | 1.00 / step_budget | (0.507, -0.001, 0.131)→(0.595, 0.184, 0.308) | (0.522, -0.001, 0.118)→(0.602, 0.184, 0.284) | 0.243→0.083 | 1.00 / 17.000 | 0.146 | 0.171 |
| descend_2 | descend | 1.00 / step_budget | (0.595, 0.184, 0.308)→(0.605, 0.205, 0.235) | (0.602, 0.184, 0.284)→(0.607, 0.205, 0.140) | 0.083→0.067 | 1.00 / 15.000 | 0.133 | 0.791 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.625
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.626
- phase_breakdown.pre_grasp_score: 0.142
- phase_breakdown.lift_clear_score: 0.651
- phase_breakdown.place_score: 0.805
- grasp_place_fitness: 0.986

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.986
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.635
- **K-run variance**: 0.0290
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.226


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41935,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00634,"descend_2.place_z_offset":0.026,"lift_1.lift_height":0.11682,"transport_1.approach_height":0.1271,"transport_1.transport_speed":0.05247},"optimized_scores":{"best_composite_score":0.64605,"best_fitness_score":0.98605,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.47941,0.04403,-0.00141],"force_p95":0.49846,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72395,"mean_force":0.09106,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47278,0.04534,0.0296]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12335.0,"contact_point_centroid":[0.47106,0.06426,0.07826],"force_p95":0.08369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33785,"mean_force":0.05574,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47039,0.04512,0.07621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12746.0,"contact_point_centroid":[0.47111,0.02606,0.0804],"force_p95":0.08356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30175,"mean_force":0.05307,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47039,0.04512,0.07845]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48282,0.04809,-0.00238],"force_p95":0.20893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28853,"mean_force":0.14985,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47481,0.04556,0.02782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3165.0,"contact_point_centroid":[0.57837,0.23792,0.27972],"force_p95":0.16435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26835,"mean_force":0.13035,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57406,0.21952,0.28292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6032.0,"contact_point_centroid":[0.57713,0.20232,0.27957],"force_p95":0.11034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19671,"mean_force":0.07164,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57431,0.21994,0.28102]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12846.0,"contact_point_centroid":[0.52046,0.14427,0.2261],"force_p95":0.12296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16896,"mean_force":0.07941,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51681,0.12535,0.22575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5695.0,"contact_point_centroid":[0.47456,0.02632,0.02932],"force_p95":0.08048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16221,"mean_force":0.04535,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47439,0.04551,0.02738]},{"body_a":"world","body_b":"grasp_target","contact_count":3332.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48847,0.02289,0.16457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15245.0,"contact_point_centroid":[0.52103,0.10856,0.22794],"force_p95":0.09044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12355,"mean_force":0.06289,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51783,0.12699,0.22773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.47453,0.06494,0.02929],"force_p95":0.08148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08699,"mean_force":0.04513,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4744,0.04551,0.02739]}],"total_contact_groups":11},"final_pose_error":0.0072,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58002,0.22537,0.2241],"final_tcp_position":[0.57861,0.22703,0.25034],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.72395,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3332.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47915,0.04593,0.03234],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04583,0.02489],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29261,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19152,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13691.0,"raw_peak_contact_force":0.28853,"tcp_end":[0.47437,0.0455,0.02736],"tcp_start":[0.47437,0.0455,0.02736],"tcp_to_object_dist_end":0.00861,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.48564,0.04562,0.1239],"object_pos_start":[0.48261,0.04581,0.02494],"object_to_goal_dist_end":0.2328,"object_to_goal_dist_start":0.29258,"object_z_max":0.12379,"peak_contact_force":0.10174,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25232.0,"raw_peak_contact_force":0.72395,"subtask_id":"lift_clear","tcp_end":[0.47048,0.04514,0.13276],"tcp_start":[0.47437,0.0455,0.02736],"tcp_to_object_dist_end":0.01757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57822,0.21061,0.30764],"object_pos_start":[0.48564,0.04562,0.1239],"object_to_goal_dist_end":0.07937,"object_to_goal_dist_start":0.2328,"object_z_max":0.30747,"peak_contact_force":0.15879,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28091.0,"raw_peak_contact_force":0.16896,"tcp_end":[0.5697,0.21076,0.32852],"tcp_start":[0.47048,0.04514,0.13276],"tcp_to_object_dist_end":0.02255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.58002,0.22537,0.2241],"object_pos_start":[0.57822,0.21061,0.30764],"object_to_goal_dist_end":0.00751,"object_to_goal_dist_start":0.07937,"object_z_max":0.3077,"peak_contact_force":0.16269,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9197.0,"raw_peak_contact_force":0.26835,"subtask_id":"place","tcp_end":[0.57861,0.22703,0.25034],"tcp_start":[0.5697,0.21076,0.32852],"tcp_to_object_dist_end":0.02633,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33019,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00094,"descend_2.place_z_offset":0.04083,"lift_1.lift_height":0.10974,"transport_1.approach_height":0.1024,"transport_1.transport_speed":0.0427},"optimized_scores":{"best_composite_score":0.27939,"best_fitness_score":0.61939,"best_task_score":0.27915},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3089.0,"contact_point_centroid":[0.60932,0.22629,-0.00245],"force_p95":0.12813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80889,"mean_force":0.14019,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60307,0.21624,0.25202]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.534,-0.01946,-0.0012],"force_p95":0.47126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64295,"mean_force":0.09183,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52356,-0.02009,0.0321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10853.0,"contact_point_centroid":[0.52263,-0.03893,0.07458],"force_p95":0.09819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30993,"mean_force":0.05834,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52096,-0.02003,0.07314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9912.0,"contact_point_centroid":[0.5226,-0.00101,0.07634],"force_p95":0.10271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30871,"mean_force":0.06266,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52097,-0.02003,0.07428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.60348,0.21969,0.27073],"force_p95":0.14545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23551,"mean_force":0.10044,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59834,0.20223,0.2758]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53707,-0.02105,-0.00213],"force_p95":0.15422,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22813,"mean_force":0.13259,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52571,-0.02014,0.03089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":331.0,"contact_point_centroid":[0.60358,0.18385,0.27245],"force_p95":0.19933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21492,"mean_force":0.14305,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59833,0.2018,0.27722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11752.0,"contact_point_centroid":[0.56036,0.10464,0.19837],"force_p95":0.12524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16544,"mean_force":0.08056,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55636,0.08618,0.19937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11971.0,"contact_point_centroid":[0.55866,0.06259,0.19494],"force_p95":0.12466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15963,"mean_force":0.07984,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55451,0.08105,0.1957]},{"body_a":"world","body_b":"grasp_target","contact_count":3388.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51411,-0.01008,0.16646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5797.0,"contact_point_centroid":[0.52521,-0.00091,0.0327],"force_p95":0.06984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11778,"mean_force":0.04513,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52524,-0.02012,0.03034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6276.0,"contact_point_centroid":[0.52506,-0.03936,0.03222],"force_p95":0.06885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07815,"mean_force":0.04318,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52524,-0.02012,0.03035]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3104.0,"contact_point_centroid":[0.60374,0.21677,0.25361],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01055,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60329,0.21675,0.25137]}],"total_contact_groups":13},"final_pose_error":0.00868,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60933,0.22626,0.01602],"final_tcp_position":[0.6069,0.22543,0.24061],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.80889,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3388.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53037,-0.0202,0.03635],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.02026,0.02561],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31615,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14806,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13877.0,"raw_peak_contact_force":0.22813,"tcp_end":[0.52521,-0.02012,0.03032],"tcp_start":[0.52521,-0.02012,0.03032],"tcp_to_object_dist_end":0.01263,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":605.0,"n_steps_budget":690.0,"object_pos_end":[0.53696,-0.02007,0.11537],"object_pos_start":[0.53693,-0.02025,0.02563],"object_to_goal_dist_end":0.27435,"object_to_goal_dist_start":0.31612,"object_z_max":0.11526,"peak_contact_force":0.10666,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20914.0,"raw_peak_contact_force":0.64295,"subtask_id":"lift_clear","tcp_end":[0.52103,-0.02002,0.1275],"tcp_start":[0.52521,-0.02012,0.03032],"tcp_to_object_dist_end":0.02002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60397,0.19997,0.25682],"object_pos_start":[0.53696,-0.02007,0.11537],"object_to_goal_dist_end":0.05704,"object_to_goal_dist_start":0.27435,"object_z_max":0.25669,"peak_contact_force":0.12456,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23723.0,"raw_peak_contact_force":0.16544,"tcp_end":[0.59842,0.20009,0.28165],"tcp_start":[0.52103,-0.02002,0.1275],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":929.0,"n_steps_budget":1000.0,"object_pos_end":[0.60933,0.22626,0.01602],"object_pos_start":[0.60397,0.19997,0.25682],"object_to_goal_dist_end":0.1914,"object_to_goal_dist_start":0.05704,"object_z_max":0.25684,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7004.0,"raw_peak_contact_force":1.80889,"subtask_id":"place","tcp_end":[0.6069,0.22543,0.24061],"tcp_start":[0.59842,0.20009,0.28165],"tcp_to_object_dist_end":0.22461,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4218,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00518,"descend_2.place_z_offset":0.0443,"lift_1.lift_height":0.1092,"transport_1.approach_height":0.1727,"transport_1.transport_speed":0.03675},"optimized_scores":{"best_composite_score":0.63487,"best_fitness_score":0.97487,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.54264,-0.02686,-0.00126],"force_p95":0.40664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57492,"mean_force":0.08457,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53168,-0.0275,0.03748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10746.0,"contact_point_centroid":[0.53085,-0.0463,0.07958],"force_p95":0.09809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31372,"mean_force":0.05865,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52909,-0.02741,0.07814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9770.0,"contact_point_centroid":[0.53082,-0.00838,0.08111],"force_p95":0.1035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30517,"mean_force":0.06313,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5291,-0.02741,0.07903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5964.0,"contact_point_centroid":[0.62978,0.17307,0.24615],"force_p95":0.15213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29542,"mean_force":0.10773,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62458,0.15501,0.2483]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54568,-0.02897,-0.00218],"force_p95":0.16514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23352,"mean_force":0.13593,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53386,-0.02757,0.03625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6883.0,"contact_point_centroid":[0.62926,0.13635,0.2488],"force_p95":0.13504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22901,"mean_force":0.09916,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6242,0.15429,0.25134]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11644.0,"contact_point_centroid":[0.57286,0.06898,0.2139],"force_p95":0.14215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17839,"mean_force":0.08014,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5683,0.05045,0.21373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12362.0,"contact_point_centroid":[0.5737,0.03355,0.21557],"force_p95":0.11822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15441,"mean_force":0.07651,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56918,0.052,0.21548]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6084.0,"contact_point_centroid":[0.53307,-0.0083,0.03851],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15247,"mean_force":0.04316,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53338,-0.02755,0.03568]},{"body_a":"world","body_b":"grasp_target","contact_count":3380.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51819,-0.01382,0.1692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6620.0,"contact_point_centroid":[0.53294,-0.04685,0.03797],"force_p95":0.06959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07456,"mean_force":0.04128,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53338,-0.02755,0.03569]}],"total_contact_groups":11},"final_pose_error":0.00777,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63262,0.16291,0.1787],"final_tcp_position":[0.62901,0.16325,0.21468],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.57492,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3380.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53853,-0.02768,0.04188],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.0279,0.02546],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26028,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15739,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14508.0,"raw_peak_contact_force":0.23352,"tcp_end":[0.53336,-0.02755,0.03566],"tcp_start":[0.53336,-0.02755,0.03566],"tcp_to_object_dist_end":0.01589,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54355,-0.02752,0.11529],"object_pos_start":[0.54555,-0.02787,0.02549],"object_to_goal_dist_end":0.22092,"object_to_goal_dist_start":0.26023,"object_z_max":0.11518,"peak_contact_force":0.10663,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20664.0,"raw_peak_contact_force":0.57492,"subtask_id":"lift_clear","tcp_end":[0.52918,-0.0274,0.13214],"tcp_start":[0.53336,-0.02755,0.03566],"tcp_to_object_dist_end":0.02215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62346,0.14118,0.2875],"object_pos_start":[0.54355,-0.02752,0.11529],"object_to_goal_dist_end":0.11349,"object_to_goal_dist_start":0.22092,"object_z_max":0.28732,"peak_contact_force":0.15557,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24006.0,"raw_peak_contact_force":0.17839,"tcp_end":[0.61836,0.14095,0.31456],"tcp_start":[0.52918,-0.0274,0.13214],"tcp_to_object_dist_end":0.02754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.63262,0.16291,0.1787],"object_pos_start":[0.62346,0.14118,0.2875],"object_to_goal_dist_end":0.0027,"object_to_goal_dist_start":0.11349,"object_z_max":0.28756,"peak_contact_force":0.1144,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12847.0,"raw_peak_contact_force":0.29542,"subtask_id":"place","tcp_end":[0.62901,0.16325,0.21468],"tcp_start":[0.61836,0.14095,0.31456],"tcp_to_object_dist_end":0.03616,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```