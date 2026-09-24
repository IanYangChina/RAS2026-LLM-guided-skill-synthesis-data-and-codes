## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0853 | 0.36 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3630 | 0.36 | ✅ accepted |
| 1 | approach → descend → grasp → lift → push → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0495 | 0.27 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3628 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=0.085) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: place_goal
  target_entity: object
  metric: goal_progress
  weight: 0.2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object_approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object_approach
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
  type: lift
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
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_1
  type: approach
  generator: arc_cartesian
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
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_goal
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.085
- **task_score** (E): 0.363
- **fitness_score**: 0.655  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1229 |
| descend_1 | 1.00 | 1.00 | 0.1487 |
| grasp_1 | 1.00 | 1.00 | 0.0121 |
| lift_1 | 1.00 | 1.00 | 0.2139 |
| transport_1 | 0.67 | 0.33 | 0.2407 |
| release_1 | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.016, 0.189) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.515, -0.016, 0.189)→(0.510, -0.017, 0.041) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.017, 0.041)→(0.502, -0.017, 0.032) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 44.333 | 0.131 | 0.157 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.017, 0.032)→(0.511, -0.017, 0.246) | (0.515, -0.017, 0.026)→(0.522, -0.017, 0.233) | 0.270→0.246 | 1.00 / 39.333 | 0.075 | 0.564 |
| transport_1 | approach | 0.67 / step_budget | (0.511, -0.017, 0.246)→(0.604, 0.148, 0.316) | (0.522, -0.017, 0.233)→(0.614, 0.140, 0.245) | 0.246→0.090 | 0.33 / 10.667 | 0.033 | 0.220 |
| release_1 | release | 1.00 / step_budget | (0.604, 0.148, 0.316)→(0.601, 0.147, 0.336) | (0.614, 0.140, 0.245)→(0.623, 0.157, 0.015) | 0.090→0.157 | 1.00 / 4.000 | 0.111 | 2.418 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.485
- phase_score: 0.218
- phase_breakdown.reach_object_approach_score: 0.130
- phase_breakdown.approach_goal_score: 0.527
- phase_breakdown.lift_clearance_score: 0.103
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.722

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.722
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.485
- **Median Q (composite search score)**: 0.078
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.288


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1,"average_solve_count":380.0,"average_success_count":380.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18379,"approach_1.arc_height":0.11037,"approach_1.speed":0.03566,"descend_1.speed":0.02463,"lift_1.lift_height":0.20013,"lift_1.speed":0.0249,"transport_1.arc_height":0.10083,"transport_1.speed":0.05172,"transport_1.transport_height":0.18504},"optimized_scores":{"best_composite_score":0.02632,"best_fitness_score":0.59632,"best_task_score":0.26375},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":399.0,"contact_point_centroid":[0.62005,0.16942,-0.00636],"force_p95":1.38521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.81661,"mean_force":0.30221,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58386,0.14742,0.4127]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.53384,-0.02116,-0.0015],"force_p95":0.35066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37005,"mean_force":0.15535,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52244,-0.02105,0.04529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12201.0,"contact_point_centroid":[0.54581,0.0328,0.3102],"force_p95":0.12367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25828,"mean_force":0.07583,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54164,0.01399,0.30944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13659.0,"contact_point_centroid":[0.54704,-0.00065,0.31408],"force_p95":0.1011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23449,"mean_force":0.06869,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54293,0.01798,0.31353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12026.0,"contact_point_centroid":[0.52586,-0.00183,0.12556],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23313,"mean_force":0.0533,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52594,-0.02101,0.12279]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12988.0,"contact_point_centroid":[0.52573,-0.04014,0.12308],"force_p95":0.07434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23221,"mean_force":0.05007,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52578,-0.02101,0.12054]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02128,-0.00203],"force_p95":0.13157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15696,"mean_force":0.12539,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52472,-0.0211,0.04597]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.53702,-0.02132,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12329,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52041,-0.01262,0.27281]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53165,-0.02131,0.13707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5090.0,"contact_point_centroid":[0.52386,-0.00183,0.04767],"force_p95":0.06568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09438,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52351,-0.02107,0.04456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5364.0,"contact_point_centroid":[0.52355,-0.04032,0.04724],"force_p95":0.06393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08057,"mean_force":0.04112,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52351,-0.02107,0.04456]}],"total_contact_groups":11},"final_pose_error":0.08527,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62029,0.16916,0.01654],"final_tcp_position":[0.58487,0.14753,0.40613],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.81661,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":736.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.53458,-0.02147,0.23332],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.53171,-0.02124,0.05422],"tcp_start":[0.53458,-0.02147,0.23332],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.02112,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31668,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13091,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12254.0,"raw_peak_contact_force":0.15696,"tcp_end":[0.52348,-0.02107,0.04452],"tcp_start":[0.53171,-0.02124,0.05422],"tcp_to_object_dist_end":0.02301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.54049,-0.02109,0.18393],"object_pos_start":[0.53693,-0.02112,0.02586],"object_to_goal_dist_end":0.25952,"object_to_goal_dist_start":0.31668,"object_z_max":0.18367,"peak_contact_force":0.07559,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25114.0,"raw_peak_contact_force":0.37005,"subtask_id":"lift_clearance","tcp_end":[0.53262,-0.02104,0.20664],"tcp_start":[0.52348,-0.02107,0.04452],"tcp_to_object_dist_end":0.02404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59616,0.13918,0.34726],"object_pos_start":[0.54049,-0.02109,0.18393],"object_to_goal_dist_end":0.16614,"object_to_goal_dist_start":0.25952,"object_z_max":0.37479,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25860.0,"raw_peak_contact_force":0.25828,"subtask_id":"approach_goal","tcp_end":[0.58487,0.14753,0.40613],"tcp_start":[0.53262,-0.02104,0.20664],"tcp_to_object_dist_end":0.06052,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62029,0.16916,0.01654],"object_pos_start":[0.59616,0.13918,0.34726],"object_to_goal_dist_end":0.19992,"object_to_goal_dist_start":0.16614,"object_z_max":0.34726,"peak_contact_force":0.13512,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":399.0,"raw_peak_contact_force":2.81661,"subtask_id":"place_goal","tcp_end":[0.58396,0.14743,0.4269],"tcp_start":[0.58487,0.14753,0.40613],"tcp_to_object_dist_end":0.41254,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28846,"average_solve_count":312.0,"average_success_count":312.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17362,"approach_1.arc_height":0.08569,"approach_1.speed":0.05039,"descend_1.speed":0.0279,"lift_1.lift_height":0.2305,"lift_1.speed":0.0602,"transport_1.arc_height":0.06085,"transport_1.speed":0.06288,"transport_1.transport_height":0.17655},"optimized_scores":{"best_composite_score":0.0777,"best_fitness_score":0.6477,"best_task_score":0.33992},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":586.0,"contact_point_centroid":[0.63942,0.14925,-0.00504],"force_p95":1.18827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.613,"mean_force":0.24471,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62175,0.14716,0.35195]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.54299,-0.02893,-0.00137],"force_p95":0.49423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59913,"mean_force":0.14238,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53112,-0.02908,0.03145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14130.0,"contact_point_centroid":[0.53558,-0.00983,0.13514],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3129,"mean_force":0.05593,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53479,-0.02892,0.13275]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14614.0,"contact_point_centroid":[0.53548,-0.04799,0.13332],"force_p95":0.07785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29814,"mean_force":0.05445,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53471,-0.02892,0.13119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7667.0,"contact_point_centroid":[0.56621,0.03749,0.30558],"force_p95":0.1486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26739,"mean_force":0.08847,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56229,0.01887,0.30566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8873.0,"contact_point_centroid":[0.56638,0.00046,0.30463],"force_p95":0.12881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24731,"mean_force":0.07883,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56228,0.01887,0.30523]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54559,-0.02913,-0.00202],"force_p95":0.12946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14486,"mean_force":0.12486,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53347,-0.02916,0.03179]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.5456,-0.02923,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53059,-0.02061,0.27298]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54268,-0.03078,0.12402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4127.0,"contact_point_centroid":[0.53283,-0.00992,0.0331],"force_p95":0.07594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09584,"mean_force":0.05169,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53222,-0.02912,0.03033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.53287,-0.04819,0.03214],"force_p95":0.06785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09041,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53222,-0.02912,0.03033]}],"total_contact_groups":11},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6399,0.14924,0.01598],"final_tcp_position":[0.62381,0.14741,0.35095],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":2.613,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":960.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.54793,-0.03248,0.22315],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.54065,-0.0294,0.04023],"tcp_start":[0.54793,-0.03248,0.22315],"tcp_to_object_dist_end":0.01505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54547,-0.02897,0.02589],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26084,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12958,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.14486,"tcp_end":[0.53218,-0.02912,0.03029],"tcp_start":[0.54065,-0.0294,0.04023],"tcp_to_object_dist_end":0.01399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.552,-0.02883,0.22504],"object_pos_start":[0.54547,-0.02897,0.02589],"object_to_goal_dist_end":0.21539,"object_to_goal_dist_start":0.26084,"object_z_max":0.2248,"peak_contact_force":0.07977,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28832.0,"raw_peak_contact_force":0.59913,"subtask_id":"lift_clearance","tcp_end":[0.54166,-0.02887,0.2368],"tcp_start":[0.53218,-0.02912,0.03029],"tcp_to_object_dist_end":0.01566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":797.0,"n_steps_budget":1000.0,"object_pos_end":[0.63388,0.13176,0.20878],"object_pos_start":[0.552,-0.02883,0.22504],"object_to_goal_dist_end":0.046,"object_to_goal_dist_start":0.21539,"object_z_max":0.33559,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16540.0,"raw_peak_contact_force":0.26739,"subtask_id":"approach_goal","tcp_end":[0.62381,0.14741,0.35095],"tcp_start":[0.54166,-0.02887,0.2368],"tcp_to_object_dist_end":0.14338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6399,0.14924,0.01598],"object_pos_start":[0.63388,0.13176,0.20878],"object_to_goal_dist_end":0.16186,"object_to_goal_dist_start":0.046,"object_z_max":0.20878,"peak_contact_force":0.12344,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":586.0,"raw_peak_contact_force":2.613,"subtask_id":"place_goal","tcp_end":[0.62171,0.1471,0.37001],"tcp_start":[0.62381,0.14741,0.35095],"tcp_to_object_dist_end":0.3545,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29268,"average_solve_count":328.0,"average_success_count":328.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06351,"approach_1.arc_height":0.0205,"approach_1.speed":0.05977,"descend_1.speed":0.03438,"lift_1.lift_height":0.28719,"lift_1.speed":0.03964,"transport_1.arc_height":0.07077,"transport_1.speed":0.05968,"transport_1.transport_height":0.05092},"optimized_scores":{"best_composite_score":0.152,"best_fitness_score":0.722,"best_task_score":0.48493},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.6064,0.1542,-0.0073],"force_p95":1.11951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82456,"mean_force":0.36875,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59769,0.14684,0.20278]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.46019,0.00048,-0.0014],"force_p95":0.61137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72304,"mean_force":0.18283,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44988,0.0003,0.02213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17881.0,"contact_point_centroid":[0.45366,0.01945,0.16191],"force_p95":0.07666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2796,"mean_force":0.05204,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45351,0.0003,0.15993]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18214.0,"contact_point_centroid":[0.45352,-0.01882,0.15907],"force_p95":0.07504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26972,"mean_force":0.0513,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45339,0.0003,0.15725]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,5e-05,-0.00203],"force_p95":0.13283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16917,"mean_force":0.12554,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45197,0.00033,0.02212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":818.0,"contact_point_centroid":[0.60107,0.12877,0.18623],"force_p95":0.10386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15588,"mean_force":0.06526,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6013,0.14796,0.18602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1290.0,"contact_point_centroid":[0.60238,0.16676,0.18657],"force_p95":0.08431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14963,"mean_force":0.04598,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60126,0.14795,0.18596]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.46286,-7e-05,-0.00191],"force_p95":0.13487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48169,0.01338,0.20762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11280.0,"contact_point_centroid":[0.5301,0.05303,0.28503],"force_p95":0.09115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13541,"mean_force":0.05837,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52886,0.07193,0.28447]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10366.0,"contact_point_centroid":[0.53793,0.09822,0.2796],"force_p95":0.09012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12328,"mean_force":0.06257,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53599,0.0792,0.2783]},{"body_a":"world","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45925,0.00366,0.06756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.45072,0.01954,0.02353],"force_p95":0.06656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08823,"mean_force":0.04378,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45086,0.00032,0.02108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5146.0,"contact_point_centroid":[0.45077,-0.01891,0.02306],"force_p95":0.0655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08448,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45087,0.00032,0.02108]}],"total_contact_groups":13},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.6075,0.15303,0.01366],"final_tcp_position":[0.60351,0.1484,0.1912],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.82456,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.46356,0.00709,0.11171],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.45839,0.00043,0.02821],"tcp_start":[0.46356,0.00709,0.11171],"tcp_to_object_dist_end":0.005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,0.00034,0.02587],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23298,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.13159,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11897.0,"raw_peak_contact_force":0.16917,"tcp_end":[0.45084,0.00032,0.02105],"tcp_start":[0.45839,0.00043,0.02821],"tcp_to_object_dist_end":0.01281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":903.0,"n_steps_budget":1000.0,"object_pos_end":[0.47302,0.00036,0.28926],"object_pos_start":[0.46271,0.00034,0.02587],"object_to_goal_dist_end":0.26453,"object_to_goal_dist_start":0.23298,"object_z_max":0.28898,"peak_contact_force":0.07062,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36174.0,"raw_peak_contact_force":0.72304,"subtask_id":"lift_clearance","tcp_end":[0.45978,0.00032,0.29345],"tcp_start":[0.45084,0.00032,0.02105],"tcp_to_object_dist_end":0.01389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.61346,0.14777,0.1785],"object_pos_start":[0.47302,0.00036,0.28926],"object_to_goal_dist_end":0.05664,"object_to_goal_dist_start":0.26453,"object_z_max":0.2998,"peak_contact_force":0.09833,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21646.0,"raw_peak_contact_force":0.13541,"subtask_id":"approach_goal","tcp_end":[0.60351,0.1484,0.1912],"tcp_start":[0.45978,0.00032,0.29345],"tcp_to_object_dist_end":0.01614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6075,0.15303,0.01366],"object_pos_start":[0.61346,0.14777,0.1785],"object_to_goal_dist_end":0.10856,"object_to_goal_dist_start":0.05664,"object_z_max":0.1785,"peak_contact_force":0.07375,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2310.0,"raw_peak_contact_force":1.82456,"subtask_id":"place_goal","tcp_end":[0.59765,0.14683,0.21051],"tcp_start":[0.60351,0.1484,0.1912],"tcp_to_object_dist_end":0.1972,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```