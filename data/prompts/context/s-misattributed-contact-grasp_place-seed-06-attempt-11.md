## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5582 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5644 | 0.81 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1996 | 0.31 | ✅ accepted |
| 8 | approach → descend → grasp → lift → push | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3137 | 0.25 | ❌ rejected |
| 7 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2166 | 0.28 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=0.558) — your mutation base

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
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  metric: goal_progress
  weight: 0.3
- id: place_object
  target_entity: object
  metric: goal_progress
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_to_grasp
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
    - 0.02
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
  guards:
  - id: grasp_check
    when: after_phase
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
    - 0.2
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_object
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
    - 0.03
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.558
- **task_score** (E): 1.000
- **fitness_score**: 0.978  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1054 |
| descend_to_grasp | 1.00 | 1.00 | 0.1668 |
| grasp_object | 1.00 | 1.00 | 0.0125 |
| lift_object | 0.67 | 1.00 | 0.1517 |
| approach_goal | 0.00 | 1.00 | 0.1168 |
| descend_to_place | 1.00 | 1.00 | 0.1019 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.202) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.021, 0.202)→(0.495, 0.024, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 42.333 | 0.153 | 0.209 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.035)→(0.486, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 36.000 | 0.093 | 0.760 |
| lift_object | lift | 0.67 / step_budget | (0.486, 0.023, 0.026)→(0.482, 0.023, 0.177) | (0.500, 0.023, 0.026)→(0.494, 0.024, 0.167) | 0.272→0.210 | 1.00 / 35.000 | 0.094 | 0.145 |
| approach_goal | approach | 0.00 / step_budget | (0.482, 0.023, 0.177)→(0.538, 0.106, 0.235) | (0.494, 0.024, 0.167)→(0.544, 0.108, 0.218) | 0.210→0.111 | 1.00 / 42.333 | 0.077 | 0.165 |
| descend_to_place | descend | 1.00 / step_budget | (0.538, 0.106, 0.235)→(0.591, 0.188, 0.228) | (0.544, 0.108, 0.218)→(0.589, 0.189, 0.205) | 0.111→0.015 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.278
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.566
- phase_breakdown.lift_object_score: 0.249
- phase_breakdown.reach_object_score: 0.295
- phase_breakdown.place_object_score: 0.864
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.558
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.388


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89583,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.13494,"approach_goal.transport_speed":0.12721,"approach_object.approach_height":0.14221,"descend_to_grasp.descend_offset":0.00031,"descend_to_place.place_z_offset":0.02468,"lift_object.lift_height":0.23199},"optimized_scores":{"best_composite_score":0.55811,"best_fitness_score":0.97811,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.50021,-0.01547,-0.0011],"force_p95":0.51054,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76014,"mean_force":0.10608,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48842,-0.0154,0.02731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17630.0,"contact_point_centroid":[0.48676,-0.03454,0.10761],"force_p95":0.08085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33676,"mean_force":0.05721,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48582,-0.01537,0.1051]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20242.0,"contact_point_centroid":[0.4875,0.00362,0.10488],"force_p95":0.07603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33257,"mean_force":0.05114,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48583,-0.01537,0.1032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19841.0,"contact_point_centroid":[0.55773,0.10797,0.25977],"force_p95":0.07115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16021,"mean_force":0.05036,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55263,0.12613,0.2594]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01575,-0.00203],"force_p95":0.13286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15816,"mean_force":0.12512,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4912,-0.01542,0.02687]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14780.0,"contact_point_centroid":[0.55169,0.14682,0.26269],"force_p95":0.09276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15189,"mean_force":0.06491,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55351,0.12779,0.25958]},{"body_a":"world","body_b":"grasp_target","contact_count":1452.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49894,-0.00667,0.24111]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4979,-0.01465,0.10723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16558.0,"contact_point_centroid":[0.50699,0.00755,0.22321],"force_p95":0.08472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11493,"mean_force":0.05897,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5039,0.02628,0.22233]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15687.0,"contact_point_centroid":[0.5052,0.04525,0.22351],"force_p95":0.0896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10707,"mean_force":0.06196,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50386,0.02624,0.22227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4148.0,"contact_point_centroid":[0.48946,-0.03468,0.02819],"force_p95":0.07892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09447,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48996,-0.01541,0.02558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5325.0,"contact_point_centroid":[0.49075,0.00365,0.02753],"force_p95":0.06666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09405,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48995,-0.01541,0.02558]}],"total_contact_groups":12},"final_pose_error":0.01884,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57572,0.17469,0.23984],"final_tcp_position":[0.57745,0.17388,0.26376],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.76014,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49986,-0.01386,0.18119],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13298,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.15816,"tcp_end":[0.49861,-0.01547,0.03471],"tcp_start":[0.49986,-0.01386,0.18119],"tcp_to_object_dist_end":0.01013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50366,-0.01576,0.02589],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31242,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.08376,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":38005.0,"raw_peak_contact_force":0.76014,"tcp_end":[0.48992,-0.01541,0.02554],"tcp_start":[0.49861,-0.01547,0.03471],"tcp_to_object_dist_end":0.01374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49785,-0.01574,0.17732],"object_pos_start":[0.50366,-0.01576,0.02589],"object_to_goal_dist_end":0.23287,"object_to_goal_dist_start":0.31242,"object_z_max":0.17713,"peak_contact_force":0.0944,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32245.0,"raw_peak_contact_force":0.11493,"subtask_id":"lift_object","tcp_end":[0.48626,-0.01536,0.1875],"tcp_start":[0.48992,-0.01541,0.02554],"tcp_to_object_dist_end":0.01543,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53128,0.06658,0.24207],"object_pos_start":[0.49785,-0.01574,0.17732],"object_to_goal_dist_end":0.13319,"object_to_goal_dist_start":0.23287,"object_z_max":0.24201,"peak_contact_force":0.07872,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34621.0,"raw_peak_contact_force":0.16021,"subtask_id":"place_object","tcp_end":[0.52341,0.06516,0.25923],"tcp_start":[0.48626,-0.01536,0.1875],"tcp_to_object_dist_end":0.01893,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57572,0.17469,0.23984],"object_pos_start":[0.53128,0.06658,0.24207],"object_to_goal_dist_end":0.01888,"object_to_goal_dist_start":0.13319,"object_z_max":0.24207,"peak_contact_force":0.12262,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1452.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.57745,0.17388,0.26376],"tcp_start":[0.52341,0.06516,0.25923],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8963,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11307,"approach_goal.transport_speed":0.14244,"approach_object.approach_height":0.19725,"descend_to_grasp.descend_offset":0.00031,"descend_to_place.place_z_offset":0.03541,"lift_object.lift_height":0.15387},"optimized_scores":{"best_composite_score":0.55785,"best_fitness_score":0.97785,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.50907,0.037,-0.00123],"force_p95":0.50293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78368,"mean_force":0.10936,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49695,0.03806,0.02724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14824.0,"contact_point_centroid":[0.49519,0.05708,0.09608],"force_p95":0.1098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35018,"mean_force":0.06192,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49437,0.03786,0.09398]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17934.0,"contact_point_centroid":[0.49659,0.01922,0.09522],"force_p95":0.08539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32739,"mean_force":0.05019,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49438,0.03786,0.09374]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51259,0.0396,-0.00214],"force_p95":0.16321,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22924,"mean_force":0.13324,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49983,0.0383,0.02667]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15266.0,"contact_point_centroid":[0.60225,0.12819,0.18847],"force_p95":0.07919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17949,"mean_force":0.04529,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59854,0.14697,0.18708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.50026,0.0192,0.02682],"force_p95":0.07364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17927,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49858,0.0382,0.02533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20594.0,"contact_point_centroid":[0.5354,0.06067,0.19019],"force_p95":0.08837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16921,"mean_force":0.04756,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53246,0.07908,0.18907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12476.0,"contact_point_centroid":[0.59613,0.16654,0.19027],"force_p95":0.08883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16691,"mean_force":0.05336,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59931,0.14772,0.1866]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14546.0,"contact_point_centroid":[0.53304,0.09888,0.19117],"force_p95":0.11578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15428,"mean_force":0.07111,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53302,0.07965,0.18943]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.51251,0.03972,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50275,0.01601,0.26635]},{"body_a":"world","body_b":"grasp_target","contact_count":2428.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50613,0.03606,0.13279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4239.0,"contact_point_centroid":[0.4989,0.05752,0.02808],"force_p95":0.08268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.091,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49859,0.0382,0.02534]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61853,0.1699,0.15157],"final_tcp_position":[0.6216,0.16953,0.17299],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.78368,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2428.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50746,0.0334,0.23274],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16033,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11044.0,"raw_peak_contact_force":0.22924,"tcp_end":[0.5073,0.0389,0.03477],"tcp_start":[0.50746,0.0334,0.23274],"tcp_to_object_dist_end":0.01022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03865,0.02552],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.11574,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":32901.0,"raw_peak_contact_force":0.78368,"tcp_end":[0.49855,0.03819,0.0253],"tcp_start":[0.5073,0.0389,0.03477],"tcp_to_object_dist_end":0.01392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.50803,0.0386,0.15665],"object_pos_start":[0.51246,0.03865,0.02552],"object_to_goal_dist_end":0.17988,"object_to_goal_dist_start":0.2132,"object_z_max":0.15653,"peak_contact_force":0.09988,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35140.0,"raw_peak_contact_force":0.16921,"subtask_id":"lift_object","tcp_end":[0.4948,0.0379,0.16695],"tcp_start":[0.49855,0.03819,0.0253],"tcp_to_object_dist_end":0.01679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57309,0.11637,0.19591],"object_pos_start":[0.50803,0.0386,0.15665],"object_to_goal_dist_end":0.09333,"object_to_goal_dist_start":0.17988,"object_z_max":0.1959,"peak_contact_force":0.07736,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27742.0,"raw_peak_contact_force":0.17949,"subtask_id":"place_object","tcp_end":[0.56853,0.11554,0.21278],"tcp_start":[0.4948,0.0379,0.16695],"tcp_to_object_dist_end":0.01749,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.61853,0.1699,0.15157],"object_pos_start":[0.57309,0.11637,0.19591],"object_to_goal_dist_end":0.01146,"object_to_goal_dist_start":0.09333,"object_z_max":0.19591,"peak_contact_force":0.12262,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.6216,0.16953,0.17299],"tcp_start":[0.56853,0.11554,0.21278],"tcp_to_object_dist_end":0.02165,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8913,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.06998,"approach_goal.transport_speed":0.14003,"approach_object.approach_height":0.15275,"descend_to_grasp.descend_offset":0.00034,"descend_to_place.place_z_offset":0.02661,"lift_object.lift_height":0.1632},"optimized_scores":{"best_composite_score":0.5587,"best_fitness_score":0.9787,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.47913,0.0457,-0.00125],"force_p95":0.47713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73626,"mean_force":0.1046,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46787,0.0468,0.02846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15861.0,"contact_point_centroid":[0.4656,0.06578,0.10397],"force_p95":0.08441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3368,"mean_force":0.05903,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46537,0.04657,0.10133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19283.0,"contact_point_centroid":[0.4678,0.02769,0.1015],"force_p95":0.08062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31491,"mean_force":0.05007,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46537,0.04656,0.10008]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04858,-0.00216],"force_p95":0.16804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23832,"mean_force":0.1347,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47063,0.04708,0.0277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.47136,0.02798,0.02774],"force_p95":0.07864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19488,"mean_force":0.04319,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46942,0.04696,0.02648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21036.0,"contact_point_centroid":[0.55539,0.16559,0.23901],"force_p95":0.07241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15583,"mean_force":0.04793,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5495,0.18366,0.2387]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18661.0,"contact_point_centroid":[0.49744,0.07528,0.20481],"force_p95":0.08264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15144,"mean_force":0.05338,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49286,0.09358,0.20447]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17919.0,"contact_point_centroid":[0.54656,0.20397,0.24262],"force_p95":0.0882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15129,"mean_force":0.05564,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55064,0.18538,0.23909]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48995,0.02068,0.24561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15178.0,"contact_point_centroid":[0.49146,0.11175,0.20585],"force_p95":0.09078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13368,"mean_force":0.06388,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49226,0.09263,0.20385]},{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47823,0.04523,0.11222]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4250.0,"contact_point_centroid":[0.46935,0.06631,0.02894],"force_p95":0.08634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09975,"mean_force":0.05206,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46942,0.04697,0.02649]}],"total_contact_groups":12},"final_pose_error":0.0156,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57193,0.22096,0.22362],"final_tcp_position":[0.57373,0.21989,0.24725],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.73626,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1960.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4812,0.04292,0.19073],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16443,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.23832,"tcp_end":[0.47785,0.04778,0.03503],"tcp_start":[0.4812,0.04292,0.19073],"tcp_to_object_dist_end":0.01028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04751,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29114,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.08072,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":35282.0,"raw_peak_contact_force":0.73626,"tcp_end":[0.46939,0.04696,0.02645],"tcp_start":[0.47785,0.04778,0.03503],"tcp_to_object_dist_end":0.01336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.47737,0.04768,0.16719],"object_pos_start":[0.4827,0.04751,0.02545],"object_to_goal_dist_end":0.21852,"object_to_goal_dist_start":0.29114,"object_z_max":0.16707,"peak_contact_force":0.08782,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33839.0,"raw_peak_contact_force":0.15144,"subtask_id":"lift_object","tcp_end":[0.46581,0.04661,0.17794],"tcp_start":[0.46939,0.04696,0.02645],"tcp_to_object_dist_end":0.01582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52684,0.13971,0.21562],"object_pos_start":[0.47737,0.04768,0.16719],"object_to_goal_dist_end":0.10581,"object_to_goal_dist_start":0.21852,"object_z_max":0.21557,"peak_contact_force":0.07456,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38955.0,"raw_peak_contact_force":0.15583,"subtask_id":"place_object","tcp_end":[0.52104,0.1375,0.23319],"tcp_start":[0.46581,0.04661,0.17794],"tcp_to_object_dist_end":0.01863,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57193,0.22096,0.22362],"object_pos_start":[0.52684,0.13971,0.21562],"object_to_goal_dist_end":0.01443,"object_to_goal_dist_start":0.10581,"object_z_max":0.22361,"peak_contact_force":0.12262,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.57373,0.21989,0.24725],"tcp_start":[0.52104,0.1375,0.23319],"tcp_to_object_dist_end":0.02372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```