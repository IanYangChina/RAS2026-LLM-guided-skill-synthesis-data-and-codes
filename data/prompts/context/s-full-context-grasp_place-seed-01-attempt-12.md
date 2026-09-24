## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → grasp → lift → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0623 | 0.61 | ❌ rejected |
| 11 | approach → align → grasp → lift → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3276 | 0.77 | ❌ rejected |
| 10 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4359 | 0.83 | ❌ rejected |
| 9 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4185 | 0.79 | ❌ rejected |
| 8 | approach → align → grasp → lift → lift → align | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0341 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.062) — your mutation base

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

- **Composite score**: 0.062
- **task_score** (E): 0.606
- **fitness_score**: 0.682  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1863 |
| descend_grasp | 1.00 | 1.00 | 0.0646 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift_to_clear | 1.00 | 1.00 | 0.0948 |
| transport_to_goal | 1.00 | 1.00 | 0.2331 |
| descend_to_goal | 1.00 | 1.00 | 0.0266 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.146 | 0.197 |
| lift_to_clear | lift | 1.00 / step_budget | (0.466, -0.001, 0.047)→(0.462, -0.001, 0.142) | (0.479, -0.001, 0.026)→(0.466, -0.001, 0.114) | 0.278→0.258 | 1.00 / 40.333 | 0.081 | 0.404 |
| transport_to_goal | lift | 1.00 / step_budget | (0.462, -0.001, 0.142)→(0.586, 0.186, 0.179) | (0.466, -0.001, 0.114)→(0.590, 0.177, 0.083) | 0.258→0.085 | 1.00 / 13.333 | 0.306 | 0.787 |
| descend_to_goal | descend | 1.00 / step_budget | (0.586, 0.186, 0.179)→(0.603, 0.201, 0.169) | (0.590, 0.177, 0.083)→(0.601, 0.187, 0.055) | 0.085→0.098 | 1.00 / 10.667 | 55983.992 | 0.719 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.520
- phase_score: 0.707
- phase_breakdown.lift_object_score: 0.732
- phase_breakdown.reach_object_score: 0.821
- phase_breakdown.grasp_object_score: 0.787
- phase_breakdown.reach_goal_score: 0.601
- grasp_place_fitness: 0.722

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.722
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.093
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.373


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50292,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.11689,"descend_grasp.descend_speed":0.13024,"descend_to_goal.descend_final_speed":0.07026,"descend_to_goal.final_z_offset":0.02753,"lift_to_clear.lift_speed":0.04851,"transport_to_goal.arc_height":0.05344,"transport_to_goal.place_offset_x":-0.00623,"transport_to_goal.place_offset_y":-0.00053,"transport_to_goal.place_offset_z":0.03083,"transport_to_goal.transport_speed":0.08139},"optimized_scores":{"best_composite_score":0.09295,"best_fitness_score":0.71295,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1913.0,"contact_point_centroid":[0.55936,0.2523,0.16964],"force_p95":0.13002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48636,"mean_force":0.09131,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55327,0.23423,0.17211]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.49628,0.04212,-0.00127],"force_p95":0.32951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43293,"mean_force":0.08873,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48639,0.04311,0.04753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1377.0,"contact_point_centroid":[0.55983,0.21635,0.1685],"force_p95":0.16352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35294,"mean_force":0.11935,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55352,0.23454,0.17187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20387.0,"contact_point_centroid":[0.48433,0.06199,0.08928],"force_p95":0.07633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28928,"mean_force":0.05044,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48398,0.0429,0.08794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19069.0,"contact_point_centroid":[0.48363,0.02375,0.09],"force_p95":0.07846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26519,"mean_force":0.05297,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48396,0.0429,0.089]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8872.0,"contact_point_centroid":[0.5125,0.13433,0.17799],"force_p95":0.10831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23466,"mean_force":0.07104,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50819,0.1159,0.17819]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22305,"mean_force":0.13351,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48926,0.04337,0.04693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7789.0,"contact_point_centroid":[0.50918,0.09157,0.17453],"force_p95":0.13464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17938,"mean_force":0.08352,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50613,0.11032,0.1759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.48841,0.02404,0.0475],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13944,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48813,0.04327,0.0457]},{"body_a":"world","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49757,0.02037,0.20882]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49546,0.04262,0.08617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5271.0,"contact_point_centroid":[0.4888,0.06245,0.04779],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07406,"mean_force":0.04219,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.04571]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56463,0.24135,0.13232],"final_tcp_position":[0.55846,0.24064,0.16748],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2260.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49714,0.04149,0.11826],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":832.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49601,0.04398,0.05435],"tcp_start":[0.49714,0.04149,0.11826],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16034,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11401.0,"raw_peak_contact_force":0.22305,"subtask_id":"grasp_object","tcp_end":[0.4881,0.04327,0.04567],"tcp_start":[0.49601,0.04398,0.05435],"tcp_to_object_dist_end":0.02406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48778,0.04308,0.10362],"object_pos_start":[0.50116,0.04379,0.02547],"object_to_goal_dist_end":0.22012,"object_to_goal_dist_start":0.24321,"object_z_max":0.10352,"peak_contact_force":0.08784,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39644.0,"raw_peak_contact_force":0.43293,"subtask_id":"lift_object","tcp_end":[0.48401,0.04291,0.13078],"tcp_start":[0.4881,0.04327,0.04567],"tcp_to_object_dist_end":0.02742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.55589,0.22858,0.14763],"object_pos_start":[0.48778,0.04308,0.10362],"object_to_goal_dist_end":0.0184,"object_to_goal_dist_start":0.22012,"object_z_max":0.17094,"peak_contact_force":0.12847,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16661.0,"raw_peak_contact_force":0.23466,"subtask_id":"reach_goal","tcp_end":[0.54926,0.22712,0.18075],"tcp_start":[0.48401,0.04291,0.13078],"tcp_to_object_dist_end":0.0338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.56463,0.24135,0.13232],"object_pos_start":[0.55589,0.22858,0.14763],"object_to_goal_dist_end":0.01487,"object_to_goal_dist_start":0.0184,"object_z_max":0.14763,"peak_contact_force":167951.73011,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3290.0,"raw_peak_contact_force":0.48636,"subtask_id":"reach_goal","tcp_end":[0.55846,0.24064,0.16748],"tcp_start":[0.54926,0.22712,0.18075],"tcp_to_object_dist_end":0.0357,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52222,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.08779,"descend_grasp.descend_speed":0.19984,"descend_to_goal.descend_final_speed":0.06735,"descend_to_goal.final_z_offset":0.01606,"lift_to_clear.lift_speed":0.03981,"transport_to_goal.arc_height":0.0395,"transport_to_goal.place_offset_x":-0.00482,"transport_to_goal.place_offset_y":-0.00102,"transport_to_goal.place_offset_z":0.03182,"transport_to_goal.transport_speed":0.13244},"optimized_scores":{"best_composite_score":-0.0079,"best_fitness_score":0.6121,"best_task_score":0.29941},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.61103,0.11813,-0.00892],"force_p95":1.54752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83368,"mean_force":0.86442,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.61012,0.14229,0.21863]},{"body_a":"world","body_b":"grasp_target","contact_count":616.0,"contact_point_centroid":[0.61131,0.1139,-0.00311],"force_p95":0.21432,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46813,"mean_force":0.12124,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61859,0.15091,0.20643]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.47142,-0.01918,-0.00118],"force_p95":0.33757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38577,"mean_force":0.08759,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46239,-0.01952,0.04851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7060.0,"contact_point_centroid":[0.50722,0.04884,0.18496],"force_p95":0.13681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34958,"mean_force":0.08449,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50394,0.0301,0.18652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18900.0,"contact_point_centroid":[0.4597,-0.00026,0.09597],"force_p95":0.07684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25845,"mean_force":0.05391,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45992,-0.01945,0.09499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21696.0,"contact_point_centroid":[0.45945,-0.03854,0.09575],"force_p95":0.07035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25794,"mean_force":0.04736,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45991,-0.01945,0.09498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7769.0,"contact_point_centroid":[0.50929,0.0133,0.18694],"force_p95":0.12926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21305,"mean_force":0.07412,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50544,0.03171,0.18775]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.1376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17757,"mean_force":0.12663,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.465,-0.01959,0.04812]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48639,-0.00905,0.20995]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47187,-0.01908,0.08718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46343,-0.00031,0.04912],"force_p95":0.0679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09916,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46391,-0.01956,0.04702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5391.0,"contact_point_centroid":[0.46347,-0.03878,0.04883],"force_p95":0.06505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08192,"mean_force":0.041,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46391,-0.01956,0.04702]},{"body_a":"left_finger","body_b":"right_finger","contact_count":486.0,"contact_point_centroid":[0.62068,0.15238,0.20613],"force_p95":0.01407,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01596,"mean_force":0.01111,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62032,0.15237,0.20385]}],"total_contact_groups":13},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61127,0.11403,0.01601],"final_tcp_position":[0.62463,0.15577,0.19959],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.83368,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47424,-0.0185,0.11964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":214.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":856.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47154,-0.01974,0.05483],"tcp_start":[0.47424,-0.0185,0.11964],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.0197,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13645,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.17757,"subtask_id":"grasp_object","tcp_end":[0.46388,-0.01956,0.04699],"tcp_start":[0.47154,-0.01974,0.05483],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46339,-0.01961,0.11442],"object_pos_start":[0.47609,-0.0197,0.0258],"object_to_goal_dist_end":0.25675,"object_to_goal_dist_start":0.28827,"object_z_max":0.11434,"peak_contact_force":0.07682,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40758.0,"raw_peak_contact_force":0.38577,"subtask_id":"lift_object","tcp_end":[0.46001,-0.01944,0.14194],"tcp_start":[0.46388,-0.01956,0.04699],"tcp_to_object_dist_end":0.02773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.61045,0.11666,-0.00271],"object_pos_start":[0.46339,-0.01961,0.11442],"object_to_goal_dist_end":0.19847,"object_to_goal_dist_start":0.25675,"object_z_max":0.18646,"peak_contact_force":0.50726,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14896.0,"raw_peak_contact_force":1.83368,"subtask_id":"reach_goal","tcp_end":[0.61241,0.14487,0.21779],"tcp_start":[0.46001,-0.01944,0.14194],"tcp_to_object_dist_end":0.22231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.61127,0.11403,0.01601],"object_pos_start":[0.61045,0.11666,-0.00271],"object_to_goal_dist_end":0.18089,"object_to_goal_dist_start":0.19847,"object_z_max":0.01668,"peak_contact_force":0.1226,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1102.0,"raw_peak_contact_force":0.46813,"subtask_id":"reach_goal","tcp_end":[0.62463,0.15577,0.19959],"tcp_start":[0.61241,0.14487,0.21779],"tcp_to_object_dist_end":0.18873,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46821,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.18293,"descend_grasp.descend_speed":0.04101,"descend_to_goal.descend_final_speed":0.08472,"descend_to_goal.final_z_offset":0.0342,"lift_to_clear.lift_speed":0.0531,"transport_to_goal.arc_height":0.05961,"transport_to_goal.place_offset_x":-0.01981,"transport_to_goal.place_offset_y":-0.00986,"transport_to_goal.place_offset_z":0.01873,"transport_to_goal.transport_speed":0.11946},"optimized_scores":{"best_composite_score":0.10195,"best_fitness_score":0.72195,"best_task_score":0.51988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3307.0,"contact_point_centroid":[0.62838,0.2067,-0.0022],"force_p95":0.12486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20339,"mean_force":0.1336,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61282,0.19739,0.13619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.60375,0.16754,0.13357],"force_p95":0.34374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.63898,"mean_force":0.16218,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.597,0.18536,0.13803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.6031,0.20252,0.1332],"force_p95":0.21502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4245,"mean_force":0.09834,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59728,0.18572,0.13748]},{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.45547,-0.0248,-0.00118],"force_p95":0.30693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39446,"mean_force":0.07273,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.4454,-0.02544,0.04921]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8142.0,"contact_point_centroid":[0.50809,0.04219,0.1753],"force_p95":0.14065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29316,"mean_force":0.0891,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50478,0.06057,0.17731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7893.0,"contact_point_centroid":[0.50668,0.07751,0.17481],"force_p95":0.13437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29128,"mean_force":0.08997,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"lift","tcp_position_centroid":[0.50364,0.05908,0.17695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18954.0,"contact_point_centroid":[0.44256,-0.00617,0.10103],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27256,"mean_force":0.05412,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44302,-0.02534,0.10047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21323.0,"contact_point_centroid":[0.44246,-0.04442,0.10025],"force_p95":0.0742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26227,"mean_force":0.04871,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44302,-0.02534,0.09977]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02625,-0.00207],"force_p95":0.14273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19115,"mean_force":0.12785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44794,-0.02554,0.04861]},{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47841,-0.01184,0.20986]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.45494,-0.0249,0.08722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44707,-0.00629,0.04877],"force_p95":0.07275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10361,"mean_force":0.04965,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44688,-0.0255,0.04758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5176.0,"contact_point_centroid":[0.44664,-0.04465,0.04876],"force_p95":0.0671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07677,"mean_force":0.04255,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44689,-0.0255,0.04759]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3166.0,"contact_point_centroid":[0.61439,0.19826,0.13865],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01567,"mean_force":0.01056,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61402,0.19824,0.13641]}],"total_contact_groups":14},"final_pose_error":0.01125,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62856,0.20666,0.01602],"final_tcp_position":[0.62458,0.20579,0.13883],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.20339,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1960.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45789,-0.02417,0.1196],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":932.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45428,-0.02577,0.05484],"tcp_start":[0.45789,-0.02417,0.1196],"tcp_to_object_dist_end":0.02914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02571,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30329,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14128,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11330.0,"raw_peak_contact_force":0.19115,"subtask_id":"grasp_object","tcp_end":[0.44686,-0.0255,0.04756],"tcp_start":[0.45428,-0.02577,0.05484],"tcp_to_object_dist_end":0.02473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44557,-0.02565,0.12323],"object_pos_start":[0.4585,-0.02571,0.02575],"object_to_goal_dist_end":0.29806,"object_to_goal_dist_start":0.30329,"object_z_max":0.12313,"peak_contact_force":0.07708,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40435.0,"raw_peak_contact_force":0.39446,"subtask_id":"lift_object","tcp_end":[0.4431,-0.02533,0.1518],"tcp_start":[0.44686,-0.0255,0.04756],"tcp_to_object_dist_end":0.02867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.60352,0.18441,0.10389],"object_pos_start":[0.44557,-0.02565,0.12323],"object_to_goal_dist_end":0.03714,"object_to_goal_dist_start":0.29806,"object_z_max":0.16315,"peak_contact_force":0.28351,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16035.0,"raw_peak_contact_force":0.29316,"subtask_id":"reach_goal","tcp_end":[0.59745,0.18476,0.13975],"tcp_start":[0.4431,-0.02533,0.1518],"tcp_to_object_dist_end":0.03638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.62856,0.20666,0.01602],"object_pos_start":[0.60352,0.18441,0.10389],"object_to_goal_dist_end":0.09812,"object_to_goal_dist_start":0.03714,"object_z_max":0.10389,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6756.0,"raw_peak_contact_force":1.20339,"subtask_id":"reach_goal","tcp_end":[0.62458,0.20579,0.13883],"tcp_start":[0.59745,0.18476,0.13975],"tcp_to_object_dist_end":0.12288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```