## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1308 | 0.27 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1344 | 0.28 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1607 | 0.23 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2545 | 0.43 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2520 | 0.43 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=0.131) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_grasp
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
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
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
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
    orientation:
      mode: keep_current
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
- id: lift_clear
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: transport_approach
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
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.002
  subtask_id: reach_goal
- id: place_descend
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=repeat
- **transport_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.002]
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.131
- **task_score** (E): 0.266
- **fitness_score**: 0.611  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_grasp | 1.00 | 1.00 | 0.2170 |
| descend_to_grasp | 1.00 | 1.00 | 0.0533 |
| grasp | 1.00 | 1.00 | 0.0122 |
| lift_clear | 1.00 | 0.67 | 0.1203 |
| transport_to_goal | 0.00 | 1.00 | 0.0337 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.505, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.000 | 0.140 | 0.205 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.002, 0.035)→(0.497, 0.002, 0.026) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 16.000 | 4.364 | 0.697 |
| lift_clear | lift | 1.00 / step_budget | (0.497, 0.002, 0.026)→(0.493, 0.002, 0.146) | (0.511, 0.002, 0.026)→(0.508, 0.003, 0.127) | 0.246→0.217 | 0.67 / 3.667 | 0.016 | 0.216 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.493, 0.002, 0.146)→(0.500, 0.014, 0.176) | (0.508, 0.003, 0.127)→(0.513, 0.017, 0.146) | 0.217→0.204 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.346
- phase_score: 0.141
- phase_breakdown.reach_grasp_score: 0.405
- phase_breakdown.reach_goal_score: 0.028
- grasp_place_fitness: 0.650

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.650
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.346
- **Median Q (composite search score)**: 0.133
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.315


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21739,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.33159,"descend_to_grasp.descend_depth":-0.00269,"lift_clear.lift_height":0.10542,"place_descend.place_z_offset":0.01493,"transport_to_goal.arc_height":0.06026,"transport_to_goal.transport_speed":0.35344},"optimized_scores":{"best_composite_score":0.08964,"best_fitness_score":0.56964,"best_task_score":0.17782},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.45547,-0.02486,-0.00112],"force_p95":0.54026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70877,"mean_force":0.08503,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44511,-0.02548,0.02659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2334.0,"contact_point_centroid":[0.45455,-0.03249,0.14022],"force_p95":0.17484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31912,"mean_force":0.10534,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.44893,-0.01412,0.14122]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.45457,0.00441,0.14047],"force_p95":0.1783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31805,"mean_force":0.10885,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.44896,-0.01403,0.14141]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9565.0,"contact_point_centroid":[0.44475,-0.00644,0.06952],"force_p95":0.10511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29961,"mean_force":0.06457,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44265,-0.02537,0.06767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10221.0,"contact_point_centroid":[0.44477,-0.04425,0.06818],"force_p95":0.103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29395,"mean_force":0.06128,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44265,-0.02537,0.06685]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02613,-0.00207],"force_p95":0.14286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21035,"mean_force":0.12818,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44756,-0.02556,0.02582]},{"body_a":"world","body_b":"grasp_target","contact_count":2156.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.47801,-0.01202,0.19471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5046.0,"contact_point_centroid":[0.44618,-0.00628,0.02745],"force_p95":0.06654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12545,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44647,-0.02552,0.0248]},{"body_a":"world","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45458,-0.02506,0.06075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5430.0,"contact_point_centroid":[0.44604,-0.0448,0.02689],"force_p95":0.06579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08311,"mean_force":0.04122,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44648,-0.02552,0.0248]}],"total_contact_groups":10},"final_pose_error":0.2812,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.47657,0.00251,0.14893],"final_tcp_position":[0.46185,0.0027,0.17181],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.70877,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":788.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.45719,-0.02443,0.08962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13957,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12276.0,"raw_peak_contact_force":0.21035,"subtask_id":"reach_grasp","tcp_end":[0.45406,-0.02579,0.03198],"tcp_start":[0.45719,-0.02443,0.08962],"tcp_to_object_dist_end":0.00749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45843,-0.02555,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3032,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.10324,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19912.0,"raw_peak_contact_force":0.70877,"tcp_end":[0.44645,-0.02552,0.02477],"tcp_start":[0.45406,-0.02579,0.03198],"tcp_to_object_dist_end":0.01203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.46051,-0.02529,0.11015],"object_pos_start":[0.45843,-0.02555,0.02576],"object_to_goal_dist_end":0.28864,"object_to_goal_dist_start":0.3032,"object_z_max":0.11005,"peak_contact_force":0.01017,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4570.0,"raw_peak_contact_force":0.31912,"tcp_end":[0.44258,-0.02535,0.11942],"tcp_start":[0.44645,-0.02552,0.02477],"tcp_to_object_dist_end":0.02018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.47657,0.00251,0.14893],"object_pos_start":[0.46051,-0.02529,0.11015],"object_to_goal_dist_end":0.25905,"object_to_goal_dist_start":0.28864,"object_z_max":0.14933,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2156.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.46185,0.0027,0.17181],"tcp_start":[0.44258,-0.02535,0.11942],"tcp_to_object_dist_end":0.0272,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.429,"descend_to_grasp.descend_depth":0.00308,"lift_clear.lift_height":0.16493,"place_descend.place_z_offset":-0.01519,"transport_to_goal.arc_height":0.10048,"transport_to_goal.transport_speed":0.25291},"optimized_scores":{"best_composite_score":0.13277,"best_fitness_score":0.61277,"best_task_score":0.27309},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.54082,0.00072,-0.00113],"force_p95":0.50421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67232,"mean_force":0.09724,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52757,0.00082,0.02831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10833.0,"contact_point_centroid":[0.5289,-0.01785,0.0919],"force_p95":0.1392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3242,"mean_force":0.08462,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52496,0.00078,0.09111]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11583.0,"contact_point_centroid":[0.52894,0.01931,0.09257],"force_p95":0.13487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31517,"mean_force":0.08156,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52499,0.00078,0.09202]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13208,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16007,"mean_force":0.12534,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53047,0.00088,0.02812]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.5174,0.00049,0.19249]},{"body_a":"world","body_b":"grasp_target","contact_count":668.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53636,0.00098,0.06158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53046,-0.01835,0.02936],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11345,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00085,0.02669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53037,0.01993,0.02848],"force_p95":0.06814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09185,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52922,0.00085,0.0267]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.52973,0.01253,0.17195],"force_p95":0.04096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04107,"mean_force":0.04006,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52545,0.00079,0.17881]}],"total_contact_groups":9},"final_pose_error":0.25685,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.53518,0.00593,0.14516],"final_tcp_position":[0.5255,0.00079,0.17888],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":12.8661,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":668.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.53706,0.00099,0.08675],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12999,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16007,"subtask_id":"reach_grasp","tcp_end":[0.53786,0.00101,0.03672],"tcp_start":[0.53706,0.00099,0.08675],"tcp_to_object_dist_end":0.01249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":12.8661,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":22558.0,"raw_peak_contact_force":0.67232,"tcp_end":[0.52919,0.00085,0.02666],"tcp_start":[0.53786,0.00101,0.03672],"tcp_to_object_dist_end":0.01499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.53523,0.00573,0.14569],"object_pos_start":[0.54416,0.00072,0.02588],"object_to_goal_dist_end":0.1947,"object_to_goal_dist_start":0.25053,"object_z_max":0.15166,"peak_contact_force":0.0,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2.0,"raw_peak_contact_force":0.04107,"tcp_end":[0.52545,0.00079,0.17881],"tcp_start":[0.52919,0.00085,0.02666],"tcp_to_object_dist_end":0.03488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53518,0.00593,0.14516],"object_pos_start":[0.53523,0.00573,0.14569],"object_to_goal_dist_end":0.19469,"object_to_goal_dist_start":0.1947,"object_z_max":0.14569,"peak_contact_force":0.12262,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.5255,0.00079,0.17888],"tcp_start":[0.52545,0.00079,0.17881],"tcp_to_object_dist_end":0.03546,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01389,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_grasp.approach_speed":0.27948,"descend_to_grasp.descend_depth":0.0015,"lift_clear.lift_height":0.12605,"place_descend.place_z_offset":0.00483,"transport_to_goal.arc_height":0.05104,"transport_to_goal.transport_speed":0.32401},"optimized_scores":{"best_composite_score":0.16991,"best_fitness_score":0.64991,"best_task_score":0.3458},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52727,0.02846,-0.0012],"force_p95":0.50897,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7086,"mean_force":0.09853,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51427,0.02932,0.02751]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10247.0,"contact_point_centroid":[0.515,0.01039,0.07825],"force_p95":0.11059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32945,"mean_force":0.07168,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51165,0.02915,0.07677]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10517.0,"contact_point_centroid":[0.51512,0.04796,0.07711],"force_p95":0.1081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32924,"mean_force":0.07083,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51169,0.02915,0.07565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1672.0,"contact_point_centroid":[0.51499,0.014,0.15123],"force_p95":0.18143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28892,"mean_force":0.11206,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51093,0.03217,0.15473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2086.0,"contact_point_centroid":[0.5146,0.05055,0.15233],"force_p95":0.16886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28775,"mean_force":0.10211,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51113,0.03258,0.15622]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03047,-0.00212],"force_p95":0.15959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24345,"mean_force":0.13248,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51716,0.02952,0.02707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.51701,0.01024,0.02845],"force_p95":0.0806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14354,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51594,0.02944,0.02571]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_grasp","phase_type":"approach","tcp_position_centroid":[0.51098,0.01417,0.19292]},{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52316,0.02925,0.06113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.51691,0.0486,0.02749],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08869,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51594,0.02944,0.02572]}],"total_contact_groups":10},"final_pose_error":0.18441,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.52586,0.0429,0.14327],"final_tcp_position":[0.51389,0.03818,0.17677],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.7086,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":696.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52411,0.02864,0.08733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15141,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10853.0,"raw_peak_contact_force":0.24345,"subtask_id":"reach_grasp","tcp_end":[0.52442,0.03,0.03527],"tcp_start":[0.52411,0.02864,0.08733],"tcp_to_object_dist_end":0.0111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53038,0.02942,0.02559],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18471,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12228,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20910.0,"raw_peak_contact_force":0.7086,"tcp_end":[0.51591,0.02944,0.02568],"tcp_start":[0.52442,0.03,0.03527],"tcp_to_object_dist_end":0.01447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.52897,0.02924,0.12615],"object_pos_start":[0.53038,0.02942,0.02559],"object_to_goal_dist_end":0.16701,"object_to_goal_dist_start":0.18471,"object_z_max":0.12605,"peak_contact_force":0.03649,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3758.0,"raw_peak_contact_force":0.28892,"tcp_end":[0.51185,0.02917,0.13949],"tcp_start":[0.51591,0.02944,0.02568],"tcp_to_object_dist_end":0.0217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.52586,0.0429,0.14327],"object_pos_start":[0.52897,0.02924,0.12615],"object_to_goal_dist_end":0.15928,"object_to_goal_dist_start":0.16701,"object_z_max":0.15026,"peak_contact_force":0.12262,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.51389,0.03818,0.17677],"tcp_start":[0.51185,0.02917,0.13949],"tcp_to_object_dist_end":0.03589,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```