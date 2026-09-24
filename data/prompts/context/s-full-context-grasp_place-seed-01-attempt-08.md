## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → grasp → lift → lift → align | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0341 | 0.24 | ❌ rejected |
| 7 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.3944 | 0.74 | ❌ rejected |
| 6 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4727 | 0.90 | ✅ accepted |
| 5 | approach → align → grasp → lift → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0791 | 0.43 | ✅ accepted |
| 4 | approach → align → grasp → lift → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0507 | 0.35 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.034) — your mutation base

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

- **Composite score**: -0.034
- **task_score** (E): 0.238
- **fitness_score**: 0.486  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1759 |
| descend_grasp | 1.00 | 1.00 | 0.0640 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift_to_clear | 1.00 | 1.00 | 0.1005 |
| transport_high | 1.00 | 1.00 | 0.2599 |
| descend_to_goal | 1.00 | 1.00 | 0.0744 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.478, -0.000, 0.129) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.478, -0.000, 0.129)→(0.475, -0.000, 0.065) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.475, -0.000, 0.065)→(0.467, -0.001, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 28.000 | 0.158 | 0.211 |
| lift_to_clear | lift | 1.00 / step_budget | (0.467, -0.001, 0.057)→(0.464, -0.001, 0.157) | (0.479, -0.000, 0.026)→(0.472, 0.007, 0.085) | 0.278→0.253 | 1.00 / 12.333 | 55983.997 | 0.385 |
| transport_high | lift | 1.00 / step_budget | (0.464, -0.001, 0.157)→(0.597, 0.192, 0.257) | (0.472, 0.007, 0.085)→(0.503, 0.076, 0.016) | 0.253→0.224 | 1.00 / 8.667 | 91004.351 | 1.067 |
| descend_to_goal | align | 1.00 / step_budget | (0.597, 0.192, 0.257)→(0.603, 0.201, 0.183) | (0.503, 0.076, 0.016)→(0.503, 0.076, 0.016) | 0.224→0.224 | 1.00 / 8.000 | 3249.684 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.337
- phase_score: 0.617
- phase_breakdown.lift_object_score: 0.699
- phase_breakdown.reach_object_score: 0.675
- phase_breakdown.grasp_object_score: 0.750
- phase_breakdown.reach_goal_score: 0.472
- grasp_place_fitness: 0.619

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.619
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.337
- **Median Q (composite search score)**: 0.048
- **K-run variance**: 0.0235
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.302


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80292,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12266,"descend_grasp.descend_speed":0.14866,"descend_to_goal.descend_place_speed":0.04655,"descend_to_goal.place_z_offset":0.02943,"lift_to_clear.lift_speed":0.09834,"transport_high.place_offset_x":-0.00126,"transport_high.place_offset_y":-0.00024,"transport_high.transport_speed":0.22999},"optimized_scores":{"best_composite_score":0.0989,"best_fitness_score":0.6189,"best_task_score":0.33686},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1443.0,"contact_point_centroid":[0.52181,0.15679,-0.00263],"force_p95":0.31962,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57605,"mean_force":0.15183,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.53434,0.17607,0.22335]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.4991,0.04174,-0.0015],"force_p95":0.26794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30843,"mean_force":0.06485,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48705,0.04217,0.05746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2907.0,"contact_point_centroid":[0.48676,0.06027,0.09475],"force_p95":0.16421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30302,"mean_force":0.11177,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48487,0.04197,0.09891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3021.0,"contact_point_centroid":[0.48592,0.02376,0.09574],"force_p95":0.15102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28047,"mean_force":0.10461,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48486,0.04197,0.09997]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1270.0,"contact_point_centroid":[0.49892,0.08703,0.16282],"force_p95":0.17175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2763,"mean_force":0.11587,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.49337,0.06947,0.16786]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50127,0.04497,-0.00219],"force_p95":0.17946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23358,"mean_force":0.13628,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48945,0.0424,0.05706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.49702,0.04776,0.16101],"force_p95":0.17163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21752,"mean_force":0.1192,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.49203,0.06574,0.16605]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49824,0.01892,0.21532]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49652,0.04097,0.09744]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.52178,0.15698,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"align","tcp_position_centroid":[0.55699,0.23584,0.21876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2648.0,"contact_point_centroid":[0.48777,0.02353,0.05214],"force_p95":0.09855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11934,"mean_force":0.07647,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48835,0.0423,0.05586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3122.0,"contact_point_centroid":[0.48842,0.06113,0.05255],"force_p95":0.09668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09711,"mean_force":0.06722,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48836,0.0423,0.05588]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1324.0,"contact_point_centroid":[0.53784,0.18425,0.22997],"force_p95":0.01169,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01581,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.53755,0.18423,0.2277]},{"body_a":"left_finger","body_b":"right_finger","contact_count":918.0,"contact_point_centroid":[0.55743,0.23589,0.22093],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"align","tcp_position_centroid":[0.557,0.23586,0.21861]}],"total_contact_groups":14},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52178,0.15698,0.01602],"final_tcp_position":[0.55947,0.24076,0.18377],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273012.80762,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49769,0.03908,0.12842],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":123.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":492.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49651,0.04298,0.06514],"tcp_start":[0.49769,0.03908,0.12842],"tcp_to_object_dist_end":0.03946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50119,0.0434,0.02533],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24358,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17539,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7570.0,"raw_peak_contact_force":0.23358,"subtask_id":"grasp_object","tcp_end":[0.48833,0.0423,0.05583],"tcp_start":[0.49651,0.04298,0.06514],"tcp_to_object_dist_end":0.03312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":320.0,"n_steps_budget":780.0,"object_pos_end":[0.49033,0.04314,0.11936],"object_pos_start":[0.50119,0.0434,0.02533],"object_to_goal_dist_end":0.21664,"object_to_goal_dist_start":0.24358,"object_z_max":0.11908,"peak_contact_force":167951.73011,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6010.0,"raw_peak_contact_force":0.30843,"subtask_id":"lift_object","tcp_end":[0.48471,0.04196,0.15628],"tcp_start":[0.48833,0.0423,0.05583],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":591.0,"n_steps_budget":690.0,"object_pos_end":[0.52178,0.15698,0.01602],"object_pos_start":[0.49033,0.04314,0.11936],"object_to_goal_dist_end":0.16321,"object_to_goal_dist_start":0.21664,"object_z_max":0.13674,"peak_contact_force":273012.80762,"phase_name":"transport_high","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5105.0,"raw_peak_contact_force":1.57605,"subtask_id":"reach_goal","tcp_end":[0.55625,0.23191,0.25295],"tcp_start":[0.48471,0.04196,0.15628],"tcp_to_object_dist_end":0.25087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.52178,0.15698,0.01602],"object_pos_start":[0.52178,0.15698,0.01602],"object_to_goal_dist_end":0.16321,"object_to_goal_dist_start":0.16321,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1774.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55947,0.24076,0.18377],"tcp_start":[0.55625,0.23191,0.25295],"tcp_to_object_dist_end":0.19126,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03356,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12126,"descend_grasp.descend_speed":0.11123,"descend_to_goal.descend_place_speed":0.09066,"descend_to_goal.place_z_offset":0.01278,"lift_to_clear.lift_speed":0.07105,"transport_high.place_offset_x":-0.00651,"transport_high.place_offset_y":-0.00952,"transport_high.transport_speed":0.14926},"optimized_scores":{"best_composite_score":0.04769,"best_fitness_score":0.56769,"best_task_score":0.23419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.53209,0.07375,-0.00245],"force_p95":0.16624,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50148,"mean_force":0.14431,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.56378,0.08879,0.24858]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.47403,-0.01865,-0.00142],"force_p95":0.26536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30869,"mean_force":0.06863,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46381,-0.01911,0.05804]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3185.0,"contact_point_centroid":[0.46245,-0.00048,0.09776],"force_p95":0.14672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26943,"mean_force":0.10245,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46148,-0.01903,0.1017]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3620.0,"contact_point_centroid":[0.46254,-0.03742,0.09742],"force_p95":0.13974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26317,"mean_force":0.09259,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.4615,-0.01903,0.10128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1430.0,"contact_point_centroid":[0.48304,0.01781,0.16637],"force_p95":0.16527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25202,"mean_force":0.1114,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.47763,0.00014,0.17104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1154.0,"contact_point_centroid":[0.48062,-0.02052,0.16429],"force_p95":0.16888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21999,"mean_force":0.12035,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.47528,-0.00245,0.16898]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.0201,-0.00208],"force_p95":0.14645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19465,"mean_force":0.12848,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.466,-0.01916,0.05789]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.13583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4878,-0.00842,0.21615]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47391,-0.01833,0.09807]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.53215,0.07385,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"align","tcp_position_centroid":[0.61952,0.14769,0.25243]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3151.0,"contact_point_centroid":[0.46307,-0.00018,0.05313],"force_p95":0.08631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09608,"mean_force":0.06646,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46494,-0.01913,0.05681]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3710.0,"contact_point_centroid":[0.46373,-0.038,0.05333],"force_p95":0.07953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08014,"mean_force":0.05738,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46494,-0.01913,0.05681]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2085.0,"contact_point_centroid":[0.56815,0.09286,0.2545],"force_p95":0.01149,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01554,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.56779,0.09286,0.2522]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1024.0,"contact_point_centroid":[0.61998,0.14773,0.25453],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"align","tcp_position_centroid":[0.61954,0.14772,0.25223]}],"total_contact_groups":14},"final_pose_error":0.00978,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53215,0.07385,0.01602],"final_tcp_position":[0.62551,0.15523,0.2095],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.80767,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47605,-0.01743,0.12962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":504.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47284,-0.0193,0.06524],"tcp_start":[0.47605,-0.01743,0.12962],"tcp_to_object_dist_end":0.03937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47611,-0.01946,0.02572],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28815,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1454,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8661.0,"raw_peak_contact_force":0.19465,"subtask_id":"grasp_object","tcp_end":[0.46491,-0.01913,0.05678],"tcp_start":[0.47284,-0.0193,0.06524],"tcp_to_object_dist_end":0.03302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.46877,-0.01939,0.12111],"object_pos_start":[0.47611,-0.01946,0.02572],"object_to_goal_dist_end":0.25119,"object_to_goal_dist_start":0.28815,"object_z_max":0.12082,"peak_contact_force":0.13868,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6882.0,"raw_peak_contact_force":0.30869,"subtask_id":"lift_object","tcp_end":[0.46126,-0.01901,0.15717],"tcp_start":[0.46491,-0.01913,0.05678],"tcp_to_object_dist_end":0.03684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.53215,0.07385,0.01602],"object_pos_start":[0.46877,-0.01939,0.12111],"object_to_goal_dist_end":0.21774,"object_to_goal_dist_start":0.25119,"object_z_max":0.14432,"peak_contact_force":0.12263,"phase_name":"transport_high","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6793.0,"raw_peak_contact_force":1.50148,"subtask_id":"reach_goal","tcp_end":[0.61538,0.14125,0.29485],"tcp_start":[0.46126,-0.01901,0.15717],"tcp_to_object_dist_end":0.29869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":241.0,"n_steps_budget":660.0,"object_pos_end":[0.53215,0.07385,0.01602],"object_pos_start":[0.53215,0.07385,0.01602],"object_to_goal_dist_end":0.21774,"object_to_goal_dist_start":0.21774,"object_z_max":0.01602,"peak_contact_force":9748.80767,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62551,0.15523,0.2095],"tcp_start":[0.61538,0.14125,0.29485],"tcp_to_object_dist_end":0.22972,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83544,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12403,"descend_grasp.descend_speed":0.0964,"descend_to_goal.descend_place_speed":0.03224,"descend_to_goal.place_z_offset":0.03512,"lift_to_clear.lift_speed":0.12216,"transport_high.place_offset_x":-0.00041,"transport_high.place_offset_y":0.00633,"transport_high.transport_speed":0.17392},"optimized_scores":{"best_composite_score":-0.24875,"best_fitness_score":0.27125,"best_task_score":0.14317},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":777.0,"contact_point_centroid":[0.45562,-0.01294,-0.00251],"force_p95":0.34144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.539,"mean_force":0.15887,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44515,-0.02478,0.11909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":468.0,"contact_point_centroid":[0.4471,-0.0063,0.05997],"force_p95":0.22496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36822,"mean_force":0.12582,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44627,-0.02485,0.06465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":737.0,"contact_point_centroid":[0.44556,-0.04268,0.06204],"force_p95":0.16755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3121,"mean_force":0.07847,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44613,-0.02484,0.06626]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4586,-0.02622,-0.0021],"force_p95":0.15502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20514,"mean_force":0.13015,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44936,-0.02497,0.0588]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48044,-0.01101,0.21622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2176.0,"contact_point_centroid":[0.44954,-0.00614,0.05367],"force_p95":0.11563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1305,"mean_force":0.09117,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44834,-0.02493,0.0578]},{"body_a":"world","body_b":"grasp_target","contact_count":3168.0,"contact_point_centroid":[0.45572,-0.00384,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1229,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.53279,0.09188,0.1896]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.4579,-0.02395,0.09825]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.45572,-0.00384,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"align","tcp_position_centroid":[0.62029,0.20406,0.18978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2998.0,"contact_point_centroid":[0.44794,-0.04338,0.05374],"force_p95":0.0939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09468,"mean_force":0.06815,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44834,-0.02493,0.0578]},{"body_a":"left_finger","body_b":"right_finger","contact_count":395.0,"contact_point_centroid":[0.44535,-0.02477,0.14388],"force_p95":0.01368,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01132,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44495,-0.02477,0.14166]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3365.0,"contact_point_centroid":[0.5335,0.09236,0.19209],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_high","phase_type":"lift","tcp_position_centroid":[0.53316,0.09236,0.18974]},{"body_a":"left_finger","body_b":"right_finger","contact_count":829.0,"contact_point_centroid":[0.62069,0.20408,0.19216],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01104,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"align","tcp_position_centroid":[0.62029,0.20407,0.18984]}],"total_contact_groups":13},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45572,-0.00384,0.01602],"final_tcp_position":[0.62389,0.20569,0.15627],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.539,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46077,-0.0228,0.12953],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":504.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45602,-0.02518,0.06569],"tcp_start":[0.46077,-0.0228,0.12953],"tcp_to_object_dist_end":0.03977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45853,-0.02528,0.02564],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30298,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15192,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6974.0,"raw_peak_contact_force":0.20514,"subtask_id":"grasp_object","tcp_end":[0.44831,-0.02493,0.05777],"tcp_start":[0.45602,-0.02518,0.06569],"tcp_to_object_dist_end":0.03372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":294.0,"n_steps_budget":630.0,"object_pos_end":[0.45572,-0.00385,0.01602],"object_pos_start":[0.45853,-0.02528,0.02564],"object_to_goal_dist_end":0.29157,"object_to_goal_dist_start":0.30298,"object_z_max":0.03908,"peak_contact_force":0.12291,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2377.0,"raw_peak_contact_force":0.539,"subtask_id":"lift_object","tcp_end":[0.44509,-0.02477,0.15815],"tcp_start":[0.44831,-0.02493,0.05777],"tcp_to_object_dist_end":0.14406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":792.0,"n_steps_budget":1000.0,"object_pos_end":[0.45572,-0.00384,0.01602],"object_pos_start":[0.45572,-0.00385,0.01602],"object_to_goal_dist_end":0.29156,"object_to_goal_dist_start":0.29157,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_high","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6533.0,"raw_peak_contact_force":0.1229,"subtask_id":"reach_goal","tcp_end":[0.61879,0.2029,0.22224],"tcp_start":[0.44509,-0.02477,0.15815],"tcp_to_object_dist_end":0.33445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.45572,-0.00384,0.01602],"object_pos_start":[0.45572,-0.00384,0.01602],"object_to_goal_dist_end":0.29156,"object_to_goal_dist_start":0.29156,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1605.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62389,0.20569,0.15627],"tcp_start":[0.61879,0.2029,0.22224],"tcp_to_object_dist_end":0.30308,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```