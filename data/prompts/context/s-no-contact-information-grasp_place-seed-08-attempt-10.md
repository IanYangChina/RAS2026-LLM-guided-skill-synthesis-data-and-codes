## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4223 | 0.74 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4265 | 0.76 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3284 | 0.56 | ✅ accepted |
| 7 | approach → descend → grasp → lift → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.2248 | 0.27 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1449 | 0.46 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.755, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.422) — your mutation base

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
  - 0.05
  weight: 0.3
- id: place_at_goal
  target_entity: object
  metric: goal_progress
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
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
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
    orientation:
      mode: keep_current
  subtask_id: reach_object
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: grasp_secured
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_retained
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
  subtask_id: place_at_goal
- id: place_1
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
    - -0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.06
      - -0.01
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=grasp_secured, when=before_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retained, when=before_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.422
- **task_score** (E): 0.741
- **fitness_score**: 0.842  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1587 |
| descend_1 | 1.00 | 0.1016 |
| grasp_1 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 0.1068 |
| transport_1 | 1.00 | 0.2576 |
| place_1 | 1.00 | 0.0464 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.046) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.046)→(0.508, -0.001, 0.037) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.037)→(0.504, -0.001, 0.144) | (0.522, -0.001, 0.026)→(0.521, -0.001, 0.128) | 0.289→0.239 |
| transport_1 | approach | 1.00 / step_budget | (0.504, -0.001, 0.144)→(0.599, 0.191, 0.285) | (0.521, -0.001, 0.128)→(0.595, 0.175, 0.169) | 0.239→0.113 |
| place_1 | descend | 1.00 / step_budget | (0.599, 0.191, 0.285)→(0.603, 0.200, 0.240) | (0.595, 0.175, 0.169)→(0.597, 0.182, 0.137) | 0.113→0.082 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.693
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.742
- phase_breakdown.reach_object_score: 0.378
- phase_breakdown.place_at_goal_score: 0.899
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.553
- **K-run variance**: 0.0344
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02985,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13568,"descend_1.descend_depth":0.01491,"lift_1.lift_height":0.15502,"place_1.place_offset_z":0.02497,"place_1.place_speed":0.13646,"transport_1.transport_speed":0.18334},"optimized_scores":{"best_composite_score":0.16014,"best_fitness_score":0.58014,"best_task_score":0.2233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.5516,0.16833,-0.00303],"force_p95":0.50357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88566,"mean_force":0.16328,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55147,0.18289,0.28558]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48031,0.0465,-0.00149],"force_p95":0.46872,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52112,"mean_force":0.10759,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46935,0.04652,0.04312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6971.0,"contact_point_centroid":[0.46899,0.0653,0.10112],"force_p95":0.10847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30584,"mean_force":0.06499,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46712,0.0463,0.09915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6612.0,"contact_point_centroid":[0.46939,0.02736,0.10378],"force_p95":0.10646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27913,"mean_force":0.06749,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46713,0.0463,0.10164]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2692.0,"contact_point_centroid":[0.49323,0.06307,0.20473],"force_p95":0.16651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27064,"mean_force":0.10451,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48761,0.08176,0.20316]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04855,-0.00217],"force_p95":0.16981,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23468,"mean_force":0.13524,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4717,0.04677,0.04275]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3712.0,"contact_point_centroid":[0.49579,0.10326,0.20659],"force_p95":0.1208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17535,"mean_force":0.07824,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48962,0.08512,0.20575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5035.0,"contact_point_centroid":[0.47031,0.02743,0.04424],"force_p95":0.07119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15614,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47059,0.04666,0.04161]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49072,0.02004,0.22554]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47891,0.04438,0.0984]},{"body_a":"world","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.55159,0.16835,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5757,0.22133,0.29668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5381.0,"contact_point_centroid":[0.47039,0.06601,0.04359],"force_p95":0.07256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07557,"mean_force":0.04205,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4706,0.04666,0.04162]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1082.0,"contact_point_centroid":[0.55522,0.18801,0.29206],"force_p95":0.01254,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01568,"mean_force":0.01078,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55473,0.18799,0.28978]},{"body_a":"left_finger","body_b":"right_finger","contact_count":338.0,"contact_point_centroid":[0.57609,0.22133,0.29912],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01053,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57569,0.22131,0.2969]}],"total_contact_groups":14},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55159,0.16835,0.01602],"final_tcp_position":[0.57732,0.224,0.27428],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.48201,0.04159,0.14862],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12281,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.47834,0.0474,0.04966],"tcp_start":[0.48201,0.04159,0.14862],"tcp_to_object_dist_end":0.02408,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48266,0.04726,0.0254],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29134,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.47057,0.04666,0.04158],"tcp_start":[0.47834,0.0474,0.04966],"tcp_to_object_dist_end":0.02021,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":419.0,"n_steps_budget":990.0,"object_pos_end":[0.48317,0.04679,0.15617],"object_pos_start":[0.48266,0.04726,0.0254],"object_to_goal_dist_end":0.22002,"object_to_goal_dist_start":0.29134,"object_z_max":0.1559,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.46721,0.04631,0.17711],"tcp_start":[0.47057,0.04666,0.04158],"tcp_to_object_dist_end":0.02633,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.55159,0.16835,0.01602],"object_pos_start":[0.48317,0.04679,0.15617],"object_to_goal_dist_end":0.22488,"object_to_goal_dist_start":0.22002,"object_z_max":0.2045,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.57443,0.21886,0.31502],"tcp_start":[0.46721,0.04631,0.17711],"tcp_to_object_dist_end":0.30409,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.55159,0.16835,0.01602],"object_pos_start":[0.55159,0.16835,0.01602],"object_to_goal_dist_end":0.22488,"object_to_goal_dist_start":0.22488,"object_z_max":0.01602,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.57732,0.224,0.27428],"tcp_start":[0.57443,0.21886,0.31502],"tcp_to_object_dist_end":0.26544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33014,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1289,"descend_1.descend_depth":0.0113,"lift_1.lift_height":0.10968,"place_1.place_offset_z":0.01885,"place_1.place_speed":0.06158,"transport_1.transport_speed":0.02545},"optimized_scores":{"best_composite_score":0.55307,"best_fitness_score":0.97307,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.53409,-0.02059,-0.00137],"force_p95":0.51348,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5442,"mean_force":0.11655,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52143,-0.02067,0.03665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4395.0,"contact_point_centroid":[0.52145,-0.00165,0.07761],"force_p95":0.1099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32983,"mean_force":0.07156,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51893,-0.02062,0.07512]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":589.0,"contact_point_centroid":[0.60553,0.22456,0.25897],"force_p95":0.17693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30788,"mean_force":0.13003,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60032,0.20646,0.26271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4837.0,"contact_point_centroid":[0.52159,-0.03945,0.07581],"force_p95":0.10533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3039,"mean_force":0.06666,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51896,-0.02062,0.07416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":697.0,"contact_point_centroid":[0.60557,0.18913,0.25771],"force_p95":0.16184,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24371,"mean_force":0.11217,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60045,0.20687,0.26167]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02116,-0.00206],"force_p95":0.14017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18206,"mean_force":0.1274,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52398,-0.02072,0.03675]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11848.0,"contact_point_centroid":[0.56052,0.10661,0.19933],"force_p95":0.12331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16689,"mean_force":0.07929,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55584,0.08804,0.19889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12507.0,"contact_point_centroid":[0.56047,0.06947,0.19918],"force_p95":0.10955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15774,"mean_force":0.07588,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55582,0.08796,0.19884]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51329,-0.00886,0.22462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.52369,-0.00149,0.03808],"force_p95":0.07767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12795,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52276,-0.0207,0.03536]},{"body_a":"world","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52857,-0.01955,0.09546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.52368,-0.03979,0.03715],"force_p95":0.06978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08332,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52276,-0.0207,0.03536]}],"total_contact_groups":12},"final_pose_error":0.01966,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60965,0.21597,0.21419],"final_tcp_position":[0.60357,0.2158,0.24033],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52862,-0.01831,0.14742],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12173,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.53122,-0.02085,0.04519],"tcp_start":[0.52862,-0.01831,0.14742],"tcp_to_object_dist_end":0.02003,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02066,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31636,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.52273,-0.0207,0.03532],"tcp_start":[0.53122,-0.02085,0.04519],"tcp_to_object_dist_end":0.01709,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":298.0,"n_steps_budget":690.0,"object_pos_end":[0.53584,-0.02057,0.11201],"object_pos_start":[0.53692,-0.02066,0.02579],"object_to_goal_dist_end":0.27625,"object_to_goal_dist_start":0.31636,"object_z_max":0.11176,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51869,-0.0206,0.12567],"tcp_start":[0.52273,-0.0207,0.03532],"tcp_to_object_dist_end":0.02193,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60332,0.20004,0.25368],"object_pos_start":[0.53584,-0.02057,0.11201],"object_to_goal_dist_end":0.05439,"object_to_goal_dist_start":0.27625,"object_z_max":0.25355,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.59805,0.19974,0.27909],"tcp_start":[0.51869,-0.0206,0.12567],"tcp_to_object_dist_end":0.02595,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.60965,0.21597,0.21419],"object_pos_start":[0.60332,0.20004,0.25368],"object_to_goal_dist_end":0.01361,"object_to_goal_dist_start":0.05439,"object_z_max":0.25371,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.60357,0.2158,0.24033],"tcp_start":[0.59805,0.19974,0.27909],"tcp_to_object_dist_end":0.02685,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42308,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08393,"descend_1.descend_depth":0.01009,"lift_1.lift_height":0.11357,"place_1.place_offset_z":0.01016,"place_1.place_speed":0.07166,"transport_1.transport_speed":0.02982},"optimized_scores":{"best_composite_score":0.55383,"best_fitness_score":0.97383,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54251,-0.02814,-0.00138],"force_p95":0.53447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56914,"mean_force":0.12052,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52962,-0.02828,0.03501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4505.0,"contact_point_centroid":[0.52989,-0.00925,0.07731],"force_p95":0.1108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33006,"mean_force":0.07363,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52706,-0.02819,0.07484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4948.0,"contact_point_centroid":[0.53,-0.047,0.07556],"force_p95":0.10654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.311,"mean_force":0.06889,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52709,-0.02819,0.07392]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":823.0,"contact_point_centroid":[0.63107,0.17606,0.23099],"force_p95":0.17178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24912,"mean_force":0.12128,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62649,0.15804,0.23512]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":837.0,"contact_point_centroid":[0.63112,0.13988,0.23086],"force_p95":0.17985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23657,"mean_force":0.11814,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62651,0.15808,0.23476]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02904,-0.00209],"force_p95":0.1477,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21436,"mean_force":0.12935,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53219,-0.02836,0.0351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10601.0,"contact_point_centroid":[0.57853,0.08145,0.19158],"force_p95":0.1243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16448,"mean_force":0.08109,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57385,0.06294,0.19159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11259.0,"contact_point_centroid":[0.57799,0.04379,0.19097],"force_p95":0.12043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15809,"mean_force":0.07725,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57349,0.06226,0.19109]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51682,-0.01216,0.2244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.53202,-0.00911,0.03636],"force_p95":0.07887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13382,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53095,-0.02832,0.03365]},{"body_a":"world","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53638,-0.02681,0.09441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.53198,-0.04743,0.03542],"force_p95":0.07108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08309,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53096,-0.02832,0.03366]}],"total_contact_groups":12},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63015,0.16033,0.17995],"final_tcp_position":[0.62787,0.16083,0.20588],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.53593,-0.02514,0.14692],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12135,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.53954,-0.02857,0.0438],"tcp_start":[0.53593,-0.02514,0.14692],"tcp_to_object_dist_end":0.0188,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.02833,0.0257],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26047,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.53092,-0.02831,0.03362],"tcp_start":[0.53954,-0.02857,0.0438],"tcp_to_object_dist_end":0.01658,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":316.0,"n_steps_budget":720.0,"object_pos_end":[0.54445,-0.02821,0.11523],"object_pos_start":[0.5455,-0.02833,0.0257],"object_to_goal_dist_end":0.22118,"object_to_goal_dist_start":0.26047,"object_z_max":0.11498,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52684,-0.02817,0.12788],"tcp_start":[0.53092,-0.02831,0.03362],"tcp_to_object_dist_end":0.02168,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.63098,0.1552,0.23663],"object_pos_start":[0.54445,-0.02821,0.11523],"object_to_goal_dist_end":0.06053,"object_to_goal_dist_start":0.22118,"object_z_max":0.23652,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.62546,0.15535,0.26126],"tcp_start":[0.52684,-0.02817,0.12788],"tcp_to_object_dist_end":0.02524,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":101.0,"n_steps_budget":1000.0,"object_pos_end":[0.63015,0.16033,0.17995],"object_pos_start":[0.63098,0.1552,0.23663],"object_to_goal_dist_end":0.00613,"object_to_goal_dist_start":0.06053,"object_z_max":0.23664,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.62787,0.16083,0.20588],"tcp_start":[0.62546,0.15535,0.26126],"tcp_to_object_dist_end":0.02604,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```