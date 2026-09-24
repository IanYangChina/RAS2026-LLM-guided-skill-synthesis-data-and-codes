## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0121 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2785 | 0.41 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3531 | 0.41 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2507 | 0.20 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.3380 | 0.43 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.012) — your mutation base

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
  - 0.15
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.7
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: descend_to_grasp
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
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_descend_dist:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_object
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
  - id: grasp_hold
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_goal
- id: descend_place
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_xy_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_xy_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_goal
- id: release
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
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_descend_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_hold, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.012
- **task_score** (E): 0.188
- **fitness_score**: 0.382  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1668 |
| descend_to_grasp | 1.00 | 1.00 | 0.0764 |
| grasp | 1.00 | 1.00 | 0.0113 |
| lift | 1.00 | 1.00 | 0.1266 |
| approach_goal | 0.00 | 1.00 | 0.1213 |
| descend_place | 1.00 | 1.00 | 0.1339 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.485, 0.001, 0.063) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 25.333 | 0.179 | 0.226 |
| grasp | grasp | 1.00 / step_budget | (0.485, 0.001, 0.063)→(0.477, 0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, 0.000, 0.025) | 0.278→0.278 | 1.00 / 12.333 | 0.123 | 0.450 |
| lift | lift | 1.00 / step_budget | (0.477, 0.001, 0.055)→(0.474, 0.001, 0.182) | (0.479, 0.000, 0.025)→(0.479, 0.017, 0.052) | 0.278→0.259 | 1.00 / 8.333 | 91002.232 | 0.515 |
| approach_goal | approach | 0.00 / step_budget | (0.474, 0.001, 0.182)→(0.534, 0.097, 0.208) | (0.479, 0.017, 0.052)→(0.478, 0.037, 0.019) | 0.259→0.255 | 1.00 / 8.000 | 0.123 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.534, 0.097, 0.208)→(0.596, 0.198, 0.148) | (0.478, 0.037, 0.019)→(0.478, 0.037, 0.019) | 0.255→0.255 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.258
- phase_score: 0.650
- phase_breakdown.reach_goal_score: 0.818
- phase_breakdown.reach_object_score: 0.257
- grasp_place_fitness: 0.587

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.587
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.258
- **Median Q (composite search score)**: -0.085
- **K-run variance**: 0.0210
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.314


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8855,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":0.00055,"descend_place.place_xy_offset_y":0.01108,"descend_to_grasp.grasp_xy_offset_x":0.01558,"descend_to_grasp.grasp_xy_offset_y":0.00253,"lift.lift_height":0.10372},"optimized_scores":{"best_composite_score":0.21687,"best_fitness_score":0.58687,"best_task_score":0.25793},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2566.0,"contact_point_centroid":[0.49862,0.10375,-0.00233],"force_p95":0.12438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30039,"mean_force":0.13664,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51704,0.11391,0.17439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6899.0,"contact_point_centroid":[0.49714,0.06362,0.09617],"force_p95":0.10324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32213,"mean_force":0.07973,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49747,0.0451,0.09935]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6355.0,"contact_point_centroid":[0.49644,0.02646,0.09422],"force_p95":0.11522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31324,"mean_force":0.08536,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49751,0.0451,0.09688]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.49848,0.04574,-0.00118],"force_p95":0.23077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31268,"mean_force":0.03497,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49994,0.04532,0.05542]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2567.0,"contact_point_centroid":[0.49836,0.04451,0.14661],"force_p95":0.13687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22439,"mean_force":0.10372,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50045,0.06313,0.14989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3548.0,"contact_point_centroid":[0.50009,0.08178,0.14608],"force_p95":0.09841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18533,"mean_force":0.07566,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50061,0.06367,0.15013]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50117,0.04511,-0.00204],"force_p95":0.13534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15988,"mean_force":0.12604,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50267,0.04559,0.05482]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49769,0.02013,0.2189]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50204,0.04356,0.09961]},{"body_a":"world","body_b":"grasp_target","contact_count":3400.0,"contact_point_centroid":[0.4986,0.10385,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54359,0.20166,0.15935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2669.0,"contact_point_centroid":[0.50201,0.06425,0.05074],"force_p95":0.0998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11825,"mean_force":0.07589,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50153,0.04548,0.05352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2937.0,"contact_point_centroid":[0.50121,0.02682,0.0507],"force_p95":0.09205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09266,"mean_force":0.07,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50153,0.04548,0.05352]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2394.0,"contact_point_centroid":[0.51859,0.1172,0.17834],"force_p95":0.01132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01064,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51815,0.11719,0.17603]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3586.0,"contact_point_centroid":[0.54399,0.20168,0.16154],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01056,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54359,0.20165,0.15936]}],"total_contact_groups":14},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.4986,0.10385,0.01602],"final_tcp_position":[0.55975,0.25069,0.14008],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.30039,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49732,0.04115,0.13814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.13367,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7406.0,"raw_peak_contact_force":0.15988,"subtask_id":"reach_object","tcp_end":[0.50941,0.04621,0.0626],"tcp_start":[0.49732,0.04115,0.13814],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04544,0.02584],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24168,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12411,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13400.0,"raw_peak_contact_force":0.32213,"tcp_end":[0.5015,0.04548,0.05349],"tcp_start":[0.50941,0.04621,0.0626],"tcp_to_object_dist_end":0.02765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50087,0.04468,0.11361],"object_pos_start":[0.50109,0.04544,0.02584],"object_to_goal_dist_end":0.21263,"object_to_goal_dist_start":0.24168,"object_z_max":0.1135,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11075.0,"raw_peak_contact_force":1.30039,"tcp_end":[0.49756,0.04511,0.14511],"tcp_start":[0.5015,0.04548,0.05349],"tcp_to_object_dist_end":0.03167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4986,0.10385,0.01602],"object_pos_start":[0.50087,0.04468,0.11361],"object_to_goal_dist_end":0.20326,"object_to_goal_dist_start":0.21263,"object_z_max":0.12118,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6986.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.52664,0.142,0.18842],"tcp_start":[0.49756,0.04511,0.14511],"tcp_to_object_dist_end":0.17879,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.4986,0.10385,0.01602],"object_pos_start":[0.4986,0.10385,0.01602],"object_to_goal_dist_end":0.20326,"object_to_goal_dist_start":0.20326,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.55975,0.25069,0.14008],"tcp_start":[0.52664,0.142,0.18842],"tcp_to_object_dist_end":0.20173,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89362,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":-0.00211,"descend_place.place_xy_offset_y":-0.00036,"descend_to_grasp.grasp_xy_offset_x":0.01309,"descend_to_grasp.grasp_xy_offset_y":0.00638,"lift.lift_height":0.14909},"optimized_scores":{"best_composite_score":-0.08468,"best_fitness_score":0.28532,"best_task_score":0.16343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2917.0,"contact_point_centroid":[0.47919,0.01148,-0.00212],"force_p95":0.24685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.557,"mean_force":0.13065,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4714,-0.0142,0.13102]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.47383,0.00427,0.05637],"force_p95":0.19951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34554,"mean_force":0.11378,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47273,-0.01423,0.06096]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.47257,-0.03213,0.05859],"force_p95":0.14834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31005,"mean_force":0.07788,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47256,-0.01423,0.06202]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.01992,-0.00239],"force_p95":0.23437,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27856,"mean_force":0.14989,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47631,-0.01428,0.05647]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48661,-0.00894,0.21993]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2150.0,"contact_point_centroid":[0.47638,0.00453,0.05101],"force_p95":0.11625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13067,"mean_force":0.0909,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47521,-0.01426,0.05531]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47743,-0.0164,0.10095]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47993,0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5078,0.02834,0.21112]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47993,0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5846,0.1138,0.20174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3265.0,"contact_point_centroid":[0.47496,-0.03325,0.05222],"force_p95":0.1036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10403,"mean_force":0.06575,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47523,-0.01426,0.05534]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2531.0,"contact_point_centroid":[0.4715,-0.0142,0.14459],"force_p95":0.01128,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0161,"mean_force":0.0108,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4713,-0.01419,0.14232]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4265.0,"contact_point_centroid":[0.58483,0.11362,0.20415],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58443,0.11361,0.20184]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4267.0,"contact_point_centroid":[0.50826,0.02855,0.21352],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01045,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.508,0.02855,0.21124]}],"total_contact_groups":13},"final_pose_error":0.01373,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47993,0.01567,0.01602],"final_tcp_position":[0.61945,0.15125,0.18419],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273006.45086,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47454,-0.01833,0.13951],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.22355,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7215.0,"raw_peak_contact_force":0.27856,"subtask_id":"reach_object","tcp_end":[0.4828,-0.01438,0.06344],"tcp_start":[0.47454,-0.01833,0.13951],"tcp_to_object_dist_end":0.03844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47601,-0.0165,0.02458],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28704,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7308.0,"raw_peak_contact_force":0.557,"tcp_end":[0.47519,-0.01426,0.05528],"tcp_start":[0.4828,-0.01438,0.06344],"tcp_to_object_dist_end":0.03079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.47993,0.01567,0.01602],"object_pos_start":[0.47601,-0.0165,0.02458],"object_to_goal_dist_end":0.27171,"object_to_goal_dist_start":0.28704,"object_z_max":0.03468,"peak_contact_force":273006.45086,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8267.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47174,-0.0142,0.19267],"tcp_start":[0.47519,-0.01426,0.05528],"tcp_to_object_dist_end":0.17934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47993,0.01567,0.01602],"object_pos_start":[0.47993,0.01567,0.01602],"object_to_goal_dist_end":0.27171,"object_to_goal_dist_start":0.27171,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8265.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.54126,0.06449,0.23051],"tcp_start":[0.47174,-0.0142,0.19267],"tcp_to_object_dist_end":0.22837,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47993,0.01567,0.01602],"object_pos_start":[0.47993,0.01567,0.01602],"object_to_goal_dist_end":0.27171,"object_to_goal_dist_start":0.27171,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.61945,0.15125,0.18419],"tcp_start":[0.54126,0.06449,0.23051],"tcp_to_object_dist_end":0.25716,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90385,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.place_xy_offset_x":-0.0026,"descend_place.place_xy_offset_y":0.00602,"descend_to_grasp.grasp_xy_offset_x":0.00964,"descend_to_grasp.grasp_xy_offset_y":-0.0048,"lift.lift_height":0.16197},"optimized_scores":{"best_composite_score":-0.09578,"best_fitness_score":0.27422,"best_task_score":0.14323},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3147.0,"contact_point_centroid":[0.4555,-0.01052,-0.00213],"force_p95":0.23934,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47105,"mean_force":0.13131,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45164,-0.02936,0.14156]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.45143,-0.04792,0.05958],"force_p95":0.19925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30632,"mean_force":0.11108,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45271,-0.02942,0.06369]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1286.0,"contact_point_centroid":[0.45197,-0.01143,0.06089],"force_p95":0.13613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30177,"mean_force":0.0785,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45256,-0.02942,0.06469]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02647,-0.00223],"force_p95":0.18804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23927,"mean_force":0.13873,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45638,-0.0296,0.05764]},{"body_a":"world","body_b":"grasp_target","contact_count":1956.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47879,-0.01168,0.22]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2166.0,"contact_point_centroid":[0.45333,-0.04825,0.05285],"force_p95":0.11417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12821,"mean_force":0.09043,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45532,-0.02954,0.05658]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45938,-0.02678,0.10147]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45549,-0.0079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49511,0.03219,0.20371]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45549,-0.0079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57472,0.14498,0.15484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2905.0,"contact_point_centroid":[0.45478,-0.01086,0.05294],"force_p95":0.10022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10075,"mean_force":0.07139,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45533,-0.02955,0.05659]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2848.0,"contact_point_centroid":[0.45189,-0.02936,0.15383],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01639,"mean_force":0.01076,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45156,-0.02935,0.15155]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4250.0,"contact_point_centroid":[0.49578,0.03261,0.20601],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01049,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49542,0.03261,0.20371]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4265.0,"contact_point_centroid":[0.57522,0.14508,0.15702],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57479,0.14507,0.15477]}],"total_contact_groups":13},"final_pose_error":0.03119,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45549,-0.0079,0.02602],"final_tcp_position":[0.60764,0.19115,0.12076],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.47105,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45846,-0.02397,0.13952],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.18088,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6871.0,"raw_peak_contact_force":0.23927,"subtask_id":"reach_object","tcp_end":[0.46268,-0.02985,0.0641],"tcp_start":[0.45846,-0.02397,0.13952],"tcp_to_object_dist_end":0.03847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02841,0.0252],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30554,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8189.0,"raw_peak_contact_force":0.47105,"tcp_end":[0.45529,-0.02954,0.05655],"tcp_start":[0.46268,-0.02985,0.0641],"tcp_to_object_dist_end":0.03153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.45549,-0.0079,0.02602],"object_pos_start":[0.45849,-0.02841,0.0252],"object_to_goal_dist_end":0.29149,"object_to_goal_dist_start":0.30554,"object_z_max":0.03767,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8250.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45202,-0.02937,0.20718],"tcp_start":[0.45529,-0.02954,0.05655],"tcp_to_object_dist_end":0.18246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45549,-0.0079,0.02602],"object_pos_start":[0.45549,-0.0079,0.02602],"object_to_goal_dist_end":0.29149,"object_to_goal_dist_start":0.29149,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8265.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53539,0.08589,0.20416],"tcp_start":[0.45202,-0.02937,0.20718],"tcp_to_object_dist_end":0.21659,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45549,-0.0079,0.02602],"object_pos_start":[0.45549,-0.0079,0.02602],"object_to_goal_dist_end":0.29149,"object_to_goal_dist_start":0.29149,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1956.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.60764,0.19115,0.12076],"tcp_start":[0.53539,0.08589,0.20416],"tcp_to_object_dist_end":0.26785,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```