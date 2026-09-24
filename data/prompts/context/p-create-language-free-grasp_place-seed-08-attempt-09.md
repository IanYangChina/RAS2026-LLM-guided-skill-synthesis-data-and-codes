## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6395 | 1.00 | ✅ accepted |
| 8 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6368 | 1.00 | ✅ accepted |
| 7 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2065 | 0.29 | ✅ accepted |
| 6 | descend → grasp → lift → descend → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2419 | 0.29 | ❌ rejected |
| 5 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2314 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.640) — your mutation base

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

- **Composite score**: 0.640
- **task_score** (E): 1.000
- **fitness_score**: 0.980  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2670 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.0970 |
| transport_1 | 0.67 | 1.00 | 0.2709 |
| descend_2 | 1.00 | 1.00 | 0.0731 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.038) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.511, -0.001, 0.032)→(0.511, -0.001, 0.032) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.333 | 0.166 | 0.249 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.032)→(0.507, -0.001, 0.129) | (0.522, -0.001, 0.025)→(0.522, -0.001, 0.116) | 0.290→0.243 | 1.00 / 25.333 | 106.768 | 0.637 |
| transport_1 | approach | 0.67 / step_budget | (0.507, -0.001, 0.129)→(0.597, 0.184, 0.304) | (0.522, -0.001, 0.116)→(0.603, 0.185, 0.279) | 0.243→0.080 | 1.00 / 17.667 | 17.869 | 0.168 |
| descend_2 | descend | 1.00 / step_budget | (0.597, 0.184, 0.304)→(0.604, 0.204, 0.235) | (0.603, 0.185, 0.279)→(0.606, 0.203, 0.205) | 0.080→0.012 | 1.00 / 19.333 | 3253.530 | 0.264 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.792
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.676
- phase_breakdown.pre_grasp_score: 0.140
- phase_breakdown.lift_clear_score: 0.652
- phase_breakdown.place_score: 0.906
- grasp_place_fitness: 0.986

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.986
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.638
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.277


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39806,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00699,"descend_2.place_z_offset":0.02619,"lift_1.lift_height":0.1175,"transport_1.approach_height":0.10219,"transport_1.transport_speed":0.05806},"optimized_scores":{"best_composite_score":0.64629,"best_fitness_score":0.98629,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.47935,0.04368,-0.00142],"force_p95":0.51288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73675,"mean_force":0.09293,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47278,0.04534,0.02898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12218.0,"contact_point_centroid":[0.47113,0.06426,0.07771],"force_p95":0.08412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33856,"mean_force":0.05623,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47039,0.04512,0.07567]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12694.0,"contact_point_centroid":[0.47116,0.02608,0.0799],"force_p95":0.08398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30212,"mean_force":0.05328,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47039,0.04512,0.07799]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48282,0.04807,-0.00238],"force_p95":0.20919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28954,"mean_force":0.14998,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47481,0.04556,0.0272]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2391.0,"contact_point_centroid":[0.57908,0.24051,0.28216],"force_p95":0.14929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24654,"mean_force":0.09467,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57602,0.22275,0.28678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2045.0,"contact_point_centroid":[0.57921,0.20445,0.2835],"force_p95":0.16594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23526,"mean_force":0.10845,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57597,0.22265,0.28774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12233.0,"contact_point_centroid":[0.52399,0.14886,0.22026],"force_p95":0.1231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17213,"mean_force":0.07972,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51977,0.13031,0.22015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12370.0,"contact_point_centroid":[0.5222,0.10971,0.21756],"force_p95":0.1255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17155,"mean_force":0.07899,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5185,0.12822,0.21794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5690.0,"contact_point_centroid":[0.47455,0.02632,0.0287],"force_p95":0.08053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16199,"mean_force":0.04536,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47438,0.04551,0.02676]},{"body_a":"world","body_b":"grasp_target","contact_count":3340.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48847,0.0229,0.16423]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.47452,0.06494,0.02867],"force_p95":0.08149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08709,"mean_force":0.04517,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47439,0.04551,0.02677]}],"total_contact_groups":11},"final_pose_error":0.00494,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57997,0.22568,0.23238],"final_tcp_position":[0.57815,0.22619,0.25856],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3340.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47915,0.04593,0.03172],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.0458,0.02489],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29263,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19162,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13686.0,"raw_peak_contact_force":0.28954,"tcp_end":[0.47436,0.0455,0.02674],"tcp_start":[0.47436,0.0455,0.02674],"tcp_to_object_dist_end":0.00846,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.48593,0.04563,0.12426],"object_pos_start":[0.48261,0.04578,0.02494],"object_to_goal_dist_end":0.2325,"object_to_goal_dist_start":0.29261,"object_z_max":0.12415,"peak_contact_force":320.095,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25061.0,"raw_peak_contact_force":0.73675,"subtask_id":"lift_clear","tcp_end":[0.47047,0.04514,0.13278],"tcp_start":[0.47436,0.0455,0.02674],"tcp_to_object_dist_end":0.01766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.5823,0.22042,0.2931],"object_pos_start":[0.48593,0.04563,0.12426],"object_to_goal_dist_end":0.06318,"object_to_goal_dist_start":0.2325,"object_z_max":0.29296,"peak_contact_force":0.13141,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24603.0,"raw_peak_contact_force":0.17213,"tcp_end":[0.5753,0.22013,0.31605],"tcp_start":[0.47047,0.04514,0.13278],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.57997,0.22568,0.23238],"object_pos_start":[0.5823,0.22042,0.2931],"object_to_goal_dist_end":0.00415,"object_to_goal_dist_start":0.06318,"object_z_max":0.29314,"peak_contact_force":9760.30694,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4436.0,"raw_peak_contact_force":0.24654,"subtask_id":"place","tcp_end":[0.57815,0.22619,0.25856],"tcp_start":[0.5753,0.22013,0.31605],"tcp_to_object_dist_end":0.02625,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00225,"descend_2.place_z_offset":0.0212,"lift_1.lift_height":0.10562,"transport_1.approach_height":0.1569,"transport_1.transport_speed":0.05379},"optimized_scores":{"best_composite_score":0.6375,"best_fitness_score":0.9775,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.53413,-0.01952,-0.0012],"force_p95":0.41594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59938,"mean_force":0.08459,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52358,-0.02007,0.03537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10790.0,"contact_point_centroid":[0.5224,-0.039,0.07635],"force_p95":0.09825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30649,"mean_force":0.05838,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52099,-0.02001,0.07467]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10341.0,"contact_point_centroid":[0.52246,-0.00102,0.07867],"force_p95":0.09638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30597,"mean_force":0.05993,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52099,-0.02001,0.07666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8206.0,"contact_point_centroid":[0.60291,0.18328,0.25659],"force_p95":0.12765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24423,"mean_force":0.10733,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59771,0.20139,0.26037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7932.0,"contact_point_centroid":[0.60274,0.2191,0.25686],"force_p95":0.13435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24229,"mean_force":0.1112,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59758,0.20105,0.26092]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53707,-0.02109,-0.00213],"force_p95":0.15408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22496,"mean_force":0.13254,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52574,-0.02012,0.03412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12574.0,"contact_point_centroid":[0.55687,0.09405,0.21233],"force_p95":0.11811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16445,"mean_force":0.07669,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55262,0.07549,0.21226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13028.0,"contact_point_centroid":[0.55678,0.05707,0.21243],"force_p95":0.11252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15635,"mean_force":0.07453,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55267,0.0756,0.21237]},{"body_a":"world","body_b":"grasp_target","contact_count":3344.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5141,-0.01006,0.16822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5804.0,"contact_point_centroid":[0.52524,-0.00089,0.03591],"force_p95":0.06993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11084,"mean_force":0.04512,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52527,-0.0201,0.03358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6275.0,"contact_point_centroid":[0.52509,-0.03934,0.03544],"force_p95":0.0689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07554,"mean_force":0.04314,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52527,-0.0201,0.03359]}],"total_contact_groups":11},"final_pose_error":0.00767,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61075,0.22224,0.19137],"final_tcp_position":[0.6055,0.2223,0.2262],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.59938,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":837.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3344.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53038,-0.02018,0.03959],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0203,0.0256],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31617,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14814,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13883.0,"raw_peak_contact_force":0.22496,"tcp_end":[0.52525,-0.0201,0.03355],"tcp_start":[0.52525,-0.0201,0.03356],"tcp_to_object_dist_end":0.01414,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53602,-0.02013,0.11269],"object_pos_start":[0.53695,-0.02028,0.02563],"object_to_goal_dist_end":0.27557,"object_to_goal_dist_start":0.31615,"object_z_max":0.11258,"peak_contact_force":0.10556,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21282.0,"raw_peak_contact_force":0.59938,"subtask_id":"lift_clear","tcp_end":[0.52105,-0.02001,0.12687],"tcp_start":[0.52525,-0.0201,0.03355],"tcp_to_object_dist_end":0.02062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59587,0.1769,0.28335],"object_pos_start":[0.53602,-0.02013,0.11269],"object_to_goal_dist_end":0.09253,"object_to_goal_dist_start":0.27557,"object_z_max":0.28317,"peak_contact_force":0.12984,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25602.0,"raw_peak_contact_force":0.16445,"tcp_end":[0.59035,0.17708,0.3083],"tcp_start":[0.52105,-0.02001,0.12687],"tcp_to_object_dist_end":0.02555,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61075,0.22224,0.19137],"object_pos_start":[0.59587,0.1769,0.28335],"object_to_goal_dist_end":0.01696,"object_to_goal_dist_start":0.09253,"object_z_max":0.28342,"peak_contact_force":0.13549,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16138.0,"raw_peak_contact_force":0.24423,"subtask_id":"place","tcp_end":[0.6055,0.2223,0.2262],"tcp_start":[0.59035,0.17708,0.3083],"tcp_to_object_dist_end":0.03522,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43216,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00525,"descend_2.place_z_offset":0.04281,"lift_1.lift_height":0.10417,"transport_1.approach_height":0.12661,"transport_1.transport_speed":0.05619},"optimized_scores":{"best_composite_score":0.6348,"best_fitness_score":0.9748,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.54264,-0.02686,-0.00126],"force_p95":0.40566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57391,"mean_force":0.08452,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53168,-0.0275,0.03755]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10371.0,"contact_point_centroid":[0.53076,-0.04631,0.07777],"force_p95":0.09667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31357,"mean_force":0.05794,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52909,-0.02741,0.07632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9408.0,"contact_point_centroid":[0.5307,-0.00836,0.07922],"force_p95":0.10332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.305,"mean_force":0.06244,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5291,-0.02741,0.07711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2596.0,"contact_point_centroid":[0.63163,0.17715,0.24834],"force_p95":0.16004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30228,"mean_force":0.0972,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62669,0.15918,0.25054]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2834.0,"contact_point_centroid":[0.63147,0.14106,0.24944],"force_p95":0.154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23567,"mean_force":0.09453,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62666,0.15908,0.25163]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54568,-0.02897,-0.00218],"force_p95":0.16513,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23344,"mean_force":0.13592,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53386,-0.02757,0.03631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12029.0,"contact_point_centroid":[0.57787,0.07859,0.20112],"force_p95":0.12408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16816,"mean_force":0.07681,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57335,0.06004,0.20079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12458.0,"contact_point_centroid":[0.57817,0.04216,0.20171],"force_p95":0.10953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15728,"mean_force":0.07513,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57372,0.06067,0.20138]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6084.0,"contact_point_centroid":[0.53308,-0.0083,0.03857],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15251,"mean_force":0.04316,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53338,-0.02755,0.03575]},{"body_a":"world","body_b":"grasp_target","contact_count":3376.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51819,-0.01382,0.16925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6620.0,"contact_point_centroid":[0.53294,-0.04685,0.03803],"force_p95":0.06959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0745,"mean_force":0.04128,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53338,-0.02755,0.03576]}],"total_contact_groups":11},"final_pose_error":0.00497,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62819,0.1618,0.19116],"final_tcp_position":[0.62862,0.16259,0.22091],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":53.34576,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53853,-0.02768,0.04194],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.0279,0.02546],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26028,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15738,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14508.0,"raw_peak_contact_force":0.23344,"tcp_end":[0.53336,-0.02755,0.03572],"tcp_start":[0.53336,-0.02755,0.03572],"tcp_to_object_dist_end":0.01594,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.54362,-0.02748,0.11069],"object_pos_start":[0.54555,-0.02787,0.02549],"object_to_goal_dist_end":0.22219,"object_to_goal_dist_start":0.26023,"object_z_max":0.11058,"peak_contact_force":0.10439,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19927.0,"raw_peak_contact_force":0.57391,"subtask_id":"lift_clear","tcp_end":[0.52913,-0.0274,0.12719],"tcp_start":[0.53336,-0.02755,0.03572],"tcp_to_object_dist_end":0.02196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.63119,0.15619,0.26057],"object_pos_start":[0.54362,-0.02748,0.11069],"object_to_goal_dist_end":0.08412,"object_to_goal_dist_start":0.22219,"object_z_max":0.26045,"peak_contact_force":53.34576,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24487.0,"raw_peak_contact_force":0.16816,"tcp_end":[0.62615,0.15591,0.28704],"tcp_start":[0.52913,-0.0274,0.12719],"tcp_to_object_dist_end":0.02694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.62819,0.1618,0.19116],"object_pos_start":[0.63119,0.15619,0.26057],"object_to_goal_dist_end":0.0153,"object_to_goal_dist_start":0.08412,"object_z_max":0.26059,"peak_contact_force":0.14607,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5430.0,"raw_peak_contact_force":0.30228,"subtask_id":"place","tcp_end":[0.62862,0.16259,0.22091],"tcp_start":[0.62615,0.15591,0.28704],"tcp_to_object_dist_end":0.02976,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```