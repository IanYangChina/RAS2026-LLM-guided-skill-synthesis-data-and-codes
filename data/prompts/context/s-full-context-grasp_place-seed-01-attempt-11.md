## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → grasp → lift → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3276 | 0.77 | ❌ rejected |
| 10 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4359 | 0.83 | ❌ rejected |
| 9 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4185 | 0.79 | ❌ rejected |
| 8 | approach → align → grasp → lift → lift → align | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0341 | 0.24 | ❌ rejected |
| 7 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.3944 | 0.74 | ❌ rejected |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.328) — your mutation base

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

- **Composite score**: 0.328
- **task_score** (E): 0.770
- **fitness_score**: 0.848  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1863 |
| descend_grasp | 1.00 | 1.00 | 0.0645 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift_to_clear | 1.00 | 1.00 | 0.0970 |
| transport_to_goal | 1.00 | 1.00 | 0.2487 |
| descend_to_goal | 1.00 | 1.00 | 0.0169 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.146 | 0.197 |
| lift_to_clear | lift | 1.00 / step_budget | (0.466, -0.001, 0.047)→(0.462, -0.001, 0.144) | (0.479, -0.001, 0.026)→(0.466, -0.001, 0.116) | 0.278→0.258 | 1.00 / 39.000 | 0.080 | 0.407 |
| transport_to_goal | align | 1.00 / step_budget | (0.462, -0.001, 0.144)→(0.595, 0.197, 0.189) | (0.466, -0.001, 0.116)→(0.594, 0.194, 0.091) | 0.258→0.076 | 1.00 / 16.000 | 0.310 | 0.704 |
| descend_to_goal | descend | 1.00 / step_budget | (0.595, 0.197, 0.189)→(0.602, 0.201, 0.175) | (0.594, 0.194, 0.091)→(0.598, 0.200, 0.086) | 0.076→0.066 | 1.00 / 15.667 | 0.141 | 0.424 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.523
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.682
- phase_breakdown.lift_object_score: 0.661
- phase_breakdown.reach_object_score: 0.821
- phase_breakdown.grasp_object_score: 0.758
- phase_breakdown.reach_goal_score: 0.593
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.442
- **K-run variance**: 0.0264
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.369


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30481,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12692,"descend_grasp.descend_speed":0.06407,"descend_to_goal.descend_final_speed":0.03642,"descend_to_goal.final_z_offset":0.03148,"lift_to_clear.lift_speed":0.05671,"transport_to_goal.place_offset_x":-0.01251,"transport_to_goal.place_offset_y":0.00372,"transport_to_goal.transport_speed":0.06294},"optimized_scores":{"best_composite_score":0.44296,"best_fitness_score":0.96296,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.49718,0.04222,-0.00127],"force_p95":0.24354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47159,"mean_force":0.08046,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48636,0.0431,0.04751]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19678.0,"contact_point_centroid":[0.48483,0.06199,0.09221],"force_p95":0.07755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29461,"mean_force":0.05208,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48405,0.04291,0.09071]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1703.0,"contact_point_centroid":[0.55289,0.2568,0.1731],"force_p95":0.13313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27724,"mean_force":0.098,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55105,0.23821,0.1769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18765.0,"contact_point_centroid":[0.48425,0.02378,0.09338],"force_p95":0.07951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26953,"mean_force":0.05378,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48403,0.0429,0.09238]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22291,"mean_force":0.13349,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48931,0.04338,0.04695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1927.0,"contact_point_centroid":[0.55219,0.21998,0.17419],"force_p95":0.10044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2074,"mean_force":0.07746,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55107,0.23823,0.1769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4331.0,"contact_point_centroid":[0.48844,0.02404,0.04752],"force_p95":0.07794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13942,"mean_force":0.04959,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48818,0.04327,0.04572]},{"body_a":"world","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49755,0.02037,0.20883]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49544,0.04262,0.0862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9811.0,"contact_point_centroid":[0.51078,0.14804,0.15723],"force_p95":0.10305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11981,"mean_force":0.06231,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"align","tcp_position_centroid":[0.50972,0.12926,0.1577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9917.0,"contact_point_centroid":[0.51094,0.11287,0.15745],"force_p95":0.099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11359,"mean_force":0.06336,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"align","tcp_position_centroid":[0.51051,0.13171,0.15834]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5274.0,"contact_point_centroid":[0.48885,0.06246,0.04781],"force_p95":0.07192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07402,"mean_force":0.04217,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48818,0.04328,0.04573]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55991,0.24152,0.13905],"final_tcp_position":[0.55755,0.24153,0.1718],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.47159,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49711,0.04149,0.11821],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":720.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":860.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49605,0.04398,0.05437],"tcp_start":[0.49711,0.04149,0.11821],"tcp_to_object_dist_end":0.02883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16028,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11405.0,"raw_peak_contact_force":0.22291,"subtask_id":"grasp_object","tcp_end":[0.48815,0.04327,0.04569],"tcp_start":[0.49605,0.04398,0.05437],"tcp_to_object_dist_end":0.02405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48817,0.04325,0.1112],"object_pos_start":[0.50115,0.04379,0.02547],"object_to_goal_dist_end":0.21847,"object_to_goal_dist_start":0.24321,"object_z_max":0.11111,"peak_contact_force":0.08482,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38637.0,"raw_peak_contact_force":0.47159,"subtask_id":"lift_object","tcp_end":[0.48414,0.04292,0.1385],"tcp_start":[0.48815,0.04327,0.04569],"tcp_to_object_dist_end":0.0276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.54605,0.23428,0.15397],"object_pos_start":[0.48817,0.04325,0.1112],"object_to_goal_dist_end":0.02239,"object_to_goal_dist_start":0.21847,"object_z_max":0.15391,"peak_contact_force":0.10398,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":19728.0,"raw_peak_contact_force":0.11981,"tcp_end":[0.54433,0.23404,0.18565],"tcp_start":[0.48414,0.04292,0.1385],"tcp_to_object_dist_end":0.03173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.55991,0.24152,0.13905],"object_pos_start":[0.54605,0.23428,0.15397],"object_to_goal_dist_end":0.00954,"object_to_goal_dist_start":0.02239,"object_z_max":0.15397,"peak_contact_force":0.13979,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3630.0,"raw_peak_contact_force":0.27724,"subtask_id":"reach_goal","tcp_end":[0.55755,0.24153,0.1718],"tcp_start":[0.54433,0.23404,0.18565],"tcp_to_object_dist_end":0.03283,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41176,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.11169,"descend_grasp.descend_speed":0.16658,"descend_to_goal.descend_final_speed":0.03591,"descend_to_goal.final_z_offset":0.02947,"lift_to_clear.lift_speed":0.03043,"transport_to_goal.place_offset_x":-0.00544,"transport_to_goal.place_offset_y":0.01172,"transport_to_goal.transport_speed":0.23517},"optimized_scores":{"best_composite_score":0.09798,"best_fitness_score":0.61798,"best_task_score":0.31117},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":55.0,"contact_point_centroid":[0.60251,0.15039,-0.00756],"force_p95":1.75825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7672,"mean_force":0.93982,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"align","tcp_position_centroid":[0.61282,0.15808,0.22556]},{"body_a":"world","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.60821,0.15655,-0.00421],"force_p95":0.39046,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63238,"mean_force":0.14051,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.618,0.15986,0.22061]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7520.0,"contact_point_centroid":[0.51883,0.03186,0.17002],"force_p95":0.13037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37133,"mean_force":0.07509,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"align","tcp_position_centroid":[0.51861,0.05049,0.17221]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.47154,-0.01934,-0.00121],"force_p95":0.31226,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35593,"mean_force":0.09014,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46231,-0.01952,0.04844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7005.0,"contact_point_centroid":[0.51627,0.0669,0.16852],"force_p95":0.14255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29981,"mean_force":0.07987,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"align","tcp_position_centroid":[0.51656,0.04815,0.17105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21671.0,"contact_point_centroid":[0.45944,-0.03854,0.09498],"force_p95":0.07039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23556,"mean_force":0.04724,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45989,-0.01945,0.09421]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18888.0,"contact_point_centroid":[0.45969,-0.00026,0.09521],"force_p95":0.07674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23458,"mean_force":0.05375,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45989,-0.01945,0.09422]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13758,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17751,"mean_force":0.12662,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46498,-0.01959,0.04811]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48635,-0.00906,0.20985]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47182,-0.01909,0.08713]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46341,-0.00031,0.04913],"force_p95":0.06793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09912,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46389,-0.01956,0.04701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5391.0,"contact_point_centroid":[0.46346,-0.03878,0.04884],"force_p95":0.06506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0819,"mean_force":0.041,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46389,-0.01956,0.04701]},{"body_a":"left_finger","body_b":"right_finger","contact_count":183.0,"contact_point_centroid":[0.62039,0.15942,0.22005],"force_p95":0.01432,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01171,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62001,0.15941,0.21775]}],"total_contact_groups":13},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60832,0.15622,0.01646],"final_tcp_position":[0.62243,0.15894,0.21518],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.7672,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47415,-0.01851,0.1195],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":852.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47152,-0.01974,0.05482],"tcp_start":[0.47415,-0.01851,0.1195],"tcp_to_object_dist_end":0.02917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13643,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.17751,"subtask_id":"grasp_object","tcp_end":[0.46386,-0.01956,0.04698],"tcp_start":[0.47152,-0.01974,0.05482],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46333,-0.01961,0.11315],"object_pos_start":[0.47609,-0.01971,0.0258],"object_to_goal_dist_end":0.25716,"object_to_goal_dist_start":0.28827,"object_z_max":0.11306,"peak_contact_force":0.07753,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40732.0,"raw_peak_contact_force":0.35593,"subtask_id":"lift_object","tcp_end":[0.45996,-0.01945,0.14064],"tcp_start":[0.46386,-0.01956,0.04698],"tcp_to_object_dist_end":0.0277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.60961,0.15092,-0.00057],"object_pos_start":[0.46333,-0.01961,0.11315],"object_to_goal_dist_end":0.192,"object_to_goal_dist_start":0.25716,"object_z_max":0.17218,"peak_contact_force":0.67365,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":14580.0,"raw_peak_contact_force":1.7672,"tcp_end":[0.61443,0.16006,0.22649],"tcp_start":[0.45996,-0.01945,0.14064],"tcp_to_object_dist_end":0.22729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":78.0,"n_steps_budget":1000.0,"object_pos_end":[0.60832,0.15622,0.01646],"object_pos_start":[0.60961,0.15092,-0.00057],"object_to_goal_dist_end":0.17511,"object_to_goal_dist_start":0.192,"object_z_max":0.01668,"peak_contact_force":0.12923,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":495.0,"raw_peak_contact_force":0.63238,"subtask_id":"reach_goal","tcp_end":[0.62243,0.15894,0.21518],"tcp_start":[0.61443,0.16006,0.22649],"tcp_to_object_dist_end":0.19925,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57062,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.14655,"descend_grasp.descend_speed":0.08927,"descend_to_goal.descend_final_speed":0.04529,"descend_to_goal.final_z_offset":0.0191,"lift_to_clear.lift_speed":0.05247,"transport_to_goal.place_offset_x":0.00772,"transport_to_goal.place_offset_y":0.00227,"transport_to_goal.transport_speed":0.09742},"optimized_scores":{"best_composite_score":0.44182,"best_fitness_score":0.96182,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.45548,-0.02479,-0.00118],"force_p95":0.30546,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39247,"mean_force":0.07247,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44542,-0.02544,0.04937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":565.0,"contact_point_centroid":[0.62495,0.18168,0.14357],"force_p95":0.15396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36121,"mean_force":0.1001,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62489,0.20003,0.14799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":590.0,"contact_point_centroid":[0.62476,0.21806,0.1431],"force_p95":0.15756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28403,"mean_force":0.09916,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62489,0.20004,0.14795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18864.0,"contact_point_centroid":[0.44252,-0.00617,0.10091],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27252,"mean_force":0.05436,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44304,-0.02534,0.10043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21286.0,"contact_point_centroid":[0.44243,-0.04441,0.10021],"force_p95":0.07448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26124,"mean_force":0.0488,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44304,-0.02534,0.09978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11197.0,"contact_point_centroid":[0.52938,0.06305,0.14973],"force_p95":0.11128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22492,"mean_force":0.07382,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"align","tcp_position_centroid":[0.52874,0.08166,0.15169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10396.0,"contact_point_centroid":[0.52813,0.09937,0.14906],"force_p95":0.10817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22035,"mean_force":0.07821,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"align","tcp_position_centroid":[0.52795,0.08072,0.15165]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00207],"force_p95":0.14292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19122,"mean_force":0.12788,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44796,-0.02554,0.04877]},{"body_a":"world","body_b":"grasp_target","contact_count":2064.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4784,-0.01183,0.2099]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.45515,-0.02492,0.08734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44708,-0.00626,0.04887],"force_p95":0.0727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10427,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.0255,0.04775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5408.0,"contact_point_centroid":[0.4463,-0.04465,0.04883],"force_p95":0.06533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07671,"mean_force":0.0408,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44691,-0.0255,0.04775]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62627,0.20168,0.10217],"final_tcp_position":[0.62491,0.20211,0.13917],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.39247,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4579,-0.02418,0.11962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45431,-0.02576,0.05502],"tcp_start":[0.4579,-0.02418,0.11962],"tcp_to_object_dist_end":0.02931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02569,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14117,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11562.0,"raw_peak_contact_force":0.19122,"subtask_id":"grasp_object","tcp_end":[0.44688,-0.02549,0.04772],"tcp_start":[0.45431,-0.02576,0.05502],"tcp_to_object_dist_end":0.02486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44542,-0.02566,0.12318],"object_pos_start":[0.4585,-0.02569,0.02575],"object_to_goal_dist_end":0.29815,"object_to_goal_dist_start":0.30328,"object_z_max":0.12308,"peak_contact_force":0.07703,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40308.0,"raw_peak_contact_force":0.39247,"subtask_id":"lift_object","tcp_end":[0.44312,-0.02533,0.15196],"tcp_start":[0.44688,-0.02549,0.04772],"tcp_to_object_dist_end":0.02887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.6256,0.19732,0.11893],"object_pos_start":[0.44542,-0.02566,0.12318],"object_to_goal_dist_end":0.01274,"object_to_goal_dist_start":0.29815,"object_z_max":0.12321,"peak_contact_force":0.15222,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":21593.0,"raw_peak_contact_force":0.22492,"tcp_end":[0.62523,0.19822,0.15503],"tcp_start":[0.44312,-0.02533,0.15196],"tcp_to_object_dist_end":0.03611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.62627,0.20168,0.10217],"object_pos_start":[0.6256,0.19732,0.11893],"object_to_goal_dist_end":0.01415,"object_to_goal_dist_start":0.01274,"object_z_max":0.11893,"peak_contact_force":0.15265,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1155.0,"raw_peak_contact_force":0.36121,"subtask_id":"reach_goal","tcp_end":[0.62491,0.20211,0.13917],"tcp_start":[0.62523,0.19822,0.15503],"tcp_to_object_dist_end":0.03702,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```