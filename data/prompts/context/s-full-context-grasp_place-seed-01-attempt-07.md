## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.3944 | 0.74 | ❌ rejected |
| 6 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4727 | 0.90 | ✅ accepted |
| 5 | approach → align → grasp → lift → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0791 | 0.43 | ✅ accepted |
| 4 | approach → align → grasp → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0507 | 0.35 | ✅ accepted |
| 3 | approach → align → grasp → lift → approach → align → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2022 | 0.20 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.900, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=0.394) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.15
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.25
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_goal
  weight: 0.4
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
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: align
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
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
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
    - -0.003
  subtask_id: grasp_object
- id: lift_to_clear
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
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_to_goal
  type: lift
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
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    place_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.003]
- **lift_to_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_offset_y: status=consumed; consumers=target.offset.y (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.394
- **task_score** (E): 0.744
- **fitness_score**: 0.834  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1863 |
| descend_grasp | 1.00 | 1.00 | 0.0646 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift_to_clear | 1.00 | 1.00 | 0.1061 |
| transport_to_goal | 1.00 | 1.00 | 0.2384 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.146 | 0.197 |
| lift_to_clear | lift | 1.00 / step_budget | (0.466, -0.001, 0.047)→(0.462, -0.001, 0.153) | (0.479, -0.001, 0.026)→(0.470, -0.001, 0.124) | 0.278→0.254 | 1.00 / 29.333 | 0.101 | 0.411 |
| transport_to_goal | lift | 1.00 / step_budget | (0.462, -0.001, 0.153)→(0.592, 0.196, 0.167) | (0.470, -0.001, 0.124)→(0.588, 0.192, 0.100) | 0.254→0.057 | 1.00 / 13.000 | 0.118 | 0.705 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.041
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.712
- phase_breakdown.lift_object_score: 0.706
- phase_breakdown.reach_object_score: 0.820
- phase_breakdown.grasp_object_score: 0.758
- phase_breakdown.reach_goal_score: 0.646
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.391
- **K-run variance**: 0.0108
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.364


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88811,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.14175,"descend_grasp.descend_speed":0.06313,"lift_to_clear.lift_speed":0.09863,"transport_to_goal.place_offset_x":0.00507,"transport_to_goal.place_offset_y":0.00299,"transport_to_goal.place_offset_z":0.02661,"transport_to_goal.transport_speed":0.07097},"optimized_scores":{"best_composite_score":0.52307,"best_fitness_score":0.96307,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.49875,0.04245,-0.00124],"force_p95":0.26381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43386,"mean_force":0.06598,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48661,0.04313,0.04753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11584.0,"contact_point_centroid":[0.48685,0.06181,0.09321],"force_p95":0.10096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2979,"mean_force":0.06234,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48419,0.04291,0.09174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10572.0,"contact_point_centroid":[0.48647,0.02398,0.09444],"force_p95":0.10627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28326,"mean_force":0.06634,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48417,0.04291,0.09341]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7236.0,"contact_point_centroid":[0.52583,0.11645,0.15635],"force_p95":0.12002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23109,"mean_force":0.07802,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.51982,0.13508,0.15702]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22297,"mean_force":0.13349,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48931,0.04338,0.04686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7391.0,"contact_point_centroid":[0.52617,0.15436,0.15637],"force_p95":0.11723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18356,"mean_force":0.0763,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.52011,0.13578,0.15707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.48844,0.02404,0.04746],"force_p95":0.07798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13951,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48817,0.04328,0.04563]},{"body_a":"world","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49756,0.02038,0.20879]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49543,0.04261,0.08611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5268.0,"contact_point_centroid":[0.48881,0.06246,0.04773],"force_p95":0.07191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07405,"mean_force":0.04222,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48818,0.04328,0.04564]}],"total_contact_groups":10},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56544,0.23266,0.13202],"final_tcp_position":[0.56033,0.23265,0.1644],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.43386,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4971,0.04147,0.11828],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":720.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49605,0.04398,0.05427],"tcp_start":[0.4971,0.04147,0.11828],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2432,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16022,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11398.0,"raw_peak_contact_force":0.22297,"subtask_id":"grasp_object","tcp_end":[0.48815,0.04327,0.0456],"tcp_start":[0.49605,0.04398,0.05427],"tcp_to_object_dist_end":0.02397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.4953,0.04345,0.12672],"object_pos_start":[0.50115,0.04379,0.02547],"object_to_goal_dist_end":0.21388,"object_to_goal_dist_start":0.2432,"object_z_max":0.12661,"peak_contact_force":0.09874,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22301.0,"raw_peak_contact_force":0.43386,"subtask_id":"lift_object","tcp_end":[0.48433,0.04293,0.15393],"tcp_start":[0.48815,0.04327,0.0456],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.56544,0.23266,0.13202],"object_pos_start":[0.4953,0.04345,0.12672],"object_to_goal_dist_end":0.01918,"object_to_goal_dist_start":0.21388,"object_z_max":0.13201,"peak_contact_force":0.12931,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14627.0,"raw_peak_contact_force":0.23109,"subtask_id":"reach_goal","tcp_end":[0.56033,0.23265,0.1644],"tcp_start":[0.48433,0.04293,0.15393],"tcp_to_object_dist_end":0.03279,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27368,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.19184,"descend_grasp.descend_speed":0.04935,"lift_to_clear.lift_speed":0.06486,"transport_to_goal.place_offset_x":-0.01881,"transport_to_goal.place_offset_y":0.00589,"transport_to_goal.place_offset_z":0.00953,"transport_to_goal.transport_speed":0.05008},"optimized_scores":{"best_composite_score":0.39094,"best_fitness_score":0.83094,"best_task_score":0.73661},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.47357,-0.01942,-0.00116],"force_p95":0.25887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40406,"mean_force":0.06737,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46242,-0.01953,0.04852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16512.0,"contact_point_centroid":[0.46148,-0.0004,0.09683],"force_p95":0.10097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27594,"mean_force":0.06216,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45991,-0.01946,0.09621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18723.0,"contact_point_centroid":[0.46128,-0.03838,0.0973],"force_p95":0.08344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27293,"mean_force":0.05463,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45992,-0.01945,0.0967]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7942.0,"contact_point_centroid":[0.52588,0.04007,0.16508],"force_p95":0.12792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21256,"mean_force":0.08415,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.52141,0.05818,0.16683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6630.0,"contact_point_centroid":[0.53291,0.08453,0.16596],"force_p95":0.13516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2111,"mean_force":0.10114,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.52803,0.06616,0.16868]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17736,"mean_force":0.1266,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46501,-0.01959,0.04794]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48634,-0.00907,0.20971]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47169,-0.01908,0.08697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46344,-0.00032,0.04898],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09916,"mean_force":0.04499,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46392,-0.01957,0.04683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5389.0,"contact_point_centroid":[0.46349,-0.03878,0.04868],"force_p95":0.06506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08185,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46392,-0.01957,0.04684]}],"total_contact_groups":10},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60582,0.15302,0.15248],"final_tcp_position":[0.60056,0.15366,0.1888],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.40406,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47407,-0.01851,0.11946],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":229.0,"n_steps_budget":930.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":916.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47154,-0.01974,0.05462],"tcp_start":[0.47407,-0.01851,0.11946],"tcp_to_object_dist_end":0.02898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13634,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12029.0,"raw_peak_contact_force":0.17736,"subtask_id":"grasp_object","tcp_end":[0.46389,-0.01956,0.0468],"tcp_start":[0.47154,-0.01974,0.05462],"tcp_to_object_dist_end":0.02428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46788,-0.01978,0.12348],"object_pos_start":[0.47609,-0.01971,0.02581],"object_to_goal_dist_end":0.2514,"object_to_goal_dist_start":0.28827,"object_z_max":0.12337,"peak_contact_force":0.12835,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35391.0,"raw_peak_contact_force":0.40406,"subtask_id":"lift_object","tcp_end":[0.45997,-0.01945,0.15247],"tcp_start":[0.46389,-0.01956,0.0468],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":741.0,"n_steps_budget":1000.0,"object_pos_end":[0.60582,0.15302,0.15248],"object_pos_start":[0.46788,-0.01978,0.12348],"object_to_goal_dist_end":0.04585,"object_to_goal_dist_start":0.2514,"object_z_max":0.15245,"peak_contact_force":0.1168,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14572.0,"raw_peak_contact_force":0.21256,"subtask_id":"reach_goal","tcp_end":[0.60056,0.15366,0.1888],"tcp_start":[0.45997,-0.01945,0.15247],"tcp_to_object_dist_end":0.0367,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25967,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.14761,"descend_grasp.descend_speed":0.02483,"lift_to_clear.lift_speed":0.05229,"transport_to_goal.place_offset_x":-0.001,"transport_to_goal.place_offset_y":0.00496,"transport_to_goal.place_offset_z":0.04119,"transport_to_goal.transport_speed":0.13284},"optimized_scores":{"best_composite_score":0.2691,"best_fitness_score":0.7091,"best_task_score":0.49413},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":277.0,"contact_point_centroid":[0.59274,0.19226,-0.00492],"force_p95":0.85186,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67222,"mean_force":0.2553,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.60938,0.191,0.14709]},{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.45547,-0.0248,-0.00118],"force_p95":0.30724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39494,"mean_force":0.07279,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.4454,-0.02545,0.04918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8549.0,"contact_point_centroid":[0.50801,0.08041,0.14575],"force_p95":0.11895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29901,"mean_force":0.07448,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50853,0.06204,0.14792]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8378.0,"contact_point_centroid":[0.50669,0.04012,0.14631],"force_p95":0.14836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28064,"mean_force":0.08081,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50597,0.05873,0.14796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18958.0,"contact_point_centroid":[0.44256,-0.00617,0.10105],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27279,"mean_force":0.0541,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44302,-0.02534,0.10048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21330.0,"contact_point_centroid":[0.44247,-0.04442,0.10027],"force_p95":0.07411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26279,"mean_force":0.04869,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44301,-0.02534,0.09978]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02625,-0.00207],"force_p95":0.14271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19112,"mean_force":0.12785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44793,-0.02554,0.04859]},{"body_a":"world","body_b":"grasp_target","contact_count":2064.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4784,-0.01183,0.2099]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.4549,-0.0249,0.0874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44707,-0.00629,0.04876],"force_p95":0.07275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10358,"mean_force":0.04965,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44688,-0.0255,0.04756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5164.0,"contact_point_centroid":[0.44666,-0.04465,0.04875],"force_p95":0.06709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07677,"mean_force":0.04262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44688,-0.0255,0.04756]}],"total_contact_groups":11},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59378,0.19127,0.01627],"final_tcp_position":[0.6166,0.20035,0.14692],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.67222,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4579,-0.02418,0.11962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":968.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45426,-0.02577,0.0548],"tcp_start":[0.4579,-0.02418,0.11962],"tcp_to_object_dist_end":0.02911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02571,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3033,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14106,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11318.0,"raw_peak_contact_force":0.19112,"subtask_id":"grasp_object","tcp_end":[0.44685,-0.0255,0.04753],"tcp_start":[0.45426,-0.02577,0.0548],"tcp_to_object_dist_end":0.02471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4456,-0.02566,0.12324],"object_pos_start":[0.4585,-0.02571,0.02575],"object_to_goal_dist_end":0.29804,"object_to_goal_dist_start":0.3033,"object_z_max":0.12314,"peak_contact_force":0.07714,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40446.0,"raw_peak_contact_force":0.39494,"subtask_id":"lift_object","tcp_end":[0.44309,-0.02533,0.15177],"tcp_start":[0.44685,-0.0255,0.04753],"tcp_to_object_dist_end":0.02864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.59378,0.19127,0.01627],"object_pos_start":[0.4456,-0.02566,0.12324],"object_to_goal_dist_end":0.10574,"object_to_goal_dist_start":0.29804,"object_z_max":0.12327,"peak_contact_force":0.10717,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17204.0,"raw_peak_contact_force":1.67222,"subtask_id":"reach_goal","tcp_end":[0.6166,0.20035,0.14692],"tcp_start":[0.44309,-0.02533,0.15177],"tcp_to_object_dist_end":0.13293,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```