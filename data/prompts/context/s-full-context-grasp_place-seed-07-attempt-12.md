## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1365 | 0.19 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1399 | 0.31 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0981 | 0.24 | ✅ accepted |
| 9 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 8 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
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

## Current Skill (Q=0.136) — your mutation base

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
  weight: 0.4
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.6
phases:
- id: approach_obj
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp
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
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
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
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: continue
- id: transport
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
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_obj** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=continue, threshold=1.0
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.136
- **task_score** (E): 0.191
- **fitness_score**: 0.556  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1381 |
| descend_grasp | 1.00 | 1.00 | 0.1114 |
| grasp | 1.00 | 1.00 | 0.0124 |
| lift | 1.00 | 0.67 | 0.1259 |
| transport | 1.00 | 1.00 | 0.1951 |
| descend_place | 1.00 | 1.00 | 0.1497 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.168) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 7.623 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.019, 0.168)→(0.506, 0.022, 0.057) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.057)→(0.498, 0.021, 0.047) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.025) | 0.273→0.274 | 1.00 / 43.000 | 0.162 | 0.215 |
| lift | lift | 1.00 / step_budget | (0.506, 0.021, 0.177)→(0.518, 0.022, 0.302) | (0.511, 0.022, 0.025)→(0.522, 0.022, 0.151) | 0.274→0.217 | 0.67 / 3.667 | 91001.812 | 1.465 |
| transport | approach | 1.00 / step_budget | (0.518, 0.022, 0.302)→(0.595, 0.187, 0.355) | (0.539, 0.038, 0.059)→(0.537, 0.047, 0.016) | 0.235→0.255 | 1.00 / 8.000 | 3249.666 | 1.238 |
| descend_place | descend | 1.00 / step_budget | (0.595, 0.187, 0.355)→(0.602, 0.205, 0.206) | (0.537, 0.047, 0.016)→(0.537, 0.047, 0.016) | 0.255→0.255 | 1.00 / 8.333 | 94252.644 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.277
- phase_score: 0.440
- phase_breakdown.reach_object_score: 0.634
- phase_breakdown.reach_goal_score: 0.357
- grasp_place_fitness: 0.598

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.598
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.277
- **Median Q (composite search score)**: 0.122
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.319


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59851,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.07965,"descend_grasp.descend_z":0.0179,"descend_place.place_offset_z":-0.0199,"lift.lift_height":0.18022,"transport.arc_height":0.06874,"transport.transport_speed":0.06432},"optimized_scores":{"best_composite_score":0.17787,"best_fitness_score":0.59787,"best_task_score":0.27679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.51883,0.04194,-0.00415],"force_p95":1.98922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0322,"mean_force":0.52264,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50437,0.0379,0.12384]},{"body_a":"world","body_b":"grasp_target","contact_count":1340.0,"contact_point_centroid":[0.53602,0.06227,-0.00276],"force_p95":0.18473,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47255,"mean_force":0.14157,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56145,0.09142,0.33809]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5456.0,"contact_point_centroid":[0.5064,0.05649,0.12668],"force_p95":0.13709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29558,"mean_force":0.07722,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50297,0.03777,0.12607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5159.0,"contact_point_centroid":[0.50642,0.01895,0.12818],"force_p95":0.14383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2591,"mean_force":0.08317,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50312,0.03778,0.12807]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03961,-0.00216],"force_p95":0.16741,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2241,"mean_force":0.13434,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50055,0.03781,0.04978]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.50283,0.01585,0.23546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4325.0,"contact_point_centroid":[0.49963,0.01853,0.04932],"force_p95":0.07644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13556,"mean_force":0.04957,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49941,0.03772,0.04851]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50635,0.03566,0.11289]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.53566,0.06283,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61788,0.16302,0.23043]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5046.0,"contact_point_centroid":[0.4999,0.05694,0.0494],"force_p95":0.07438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07656,"mean_force":0.04393,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49941,0.03772,0.04852]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1366.0,"contact_point_centroid":[0.56358,0.09345,0.34184],"force_p95":0.01197,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.0107,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56307,0.09343,0.33964]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1243.0,"contact_point_centroid":[0.61836,0.16301,0.23299],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61786,0.16299,0.23088]}],"total_contact_groups":12},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.53566,0.06283,0.01602],"final_tcp_position":[0.62212,0.16919,0.14387],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.83016,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50727,0.03316,0.16813],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50757,0.03836,0.05779],"tcp_start":[0.50727,0.03316,0.16813],"tcp_to_object_dist_end":0.03218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03841,0.02542],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21338,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16355,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11171.0,"raw_peak_contact_force":0.2241,"tcp_end":[0.49938,0.03772,0.04848],"tcp_start":[0.50757,0.03836,0.05779],"tcp_to_object_dist_end":0.02653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":492.0,"n_steps_budget":990.0,"object_pos_end":[0.5229,0.03889,0.14873],"object_pos_start":[0.51249,0.03841,0.02542],"object_to_goal_dist_end":0.16978,"object_to_goal_dist_start":0.21338,"object_z_max":0.20531,"peak_contact_force":1.51655,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10711.0,"raw_peak_contact_force":2.0322,"tcp_end":[0.51895,0.03858,0.29936],"tcp_start":[0.5074,0.03801,0.17613],"tcp_to_object_dist_end":0.15069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.53566,0.06283,0.01602],"object_pos_start":[0.54074,0.05308,-0.00491],"object_to_goal_dist_end":0.19267,"object_to_goal_dist_start":0.21045,"object_z_max":0.01717,"peak_contact_force":9748.75384,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2706.0,"raw_peak_contact_force":1.47255,"subtask_id":"reach_goal","tcp_end":[0.61471,0.15733,0.31709],"tcp_start":[0.51895,0.03858,0.29936],"tcp_to_object_dist_end":0.32531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.53566,0.06283,0.01602],"object_pos_start":[0.53566,0.06283,0.01602],"object_to_goal_dist_end":0.19267,"object_to_goal_dist_start":0.19267,"object_z_max":0.01602,"peak_contact_force":9748.83016,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2407.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62212,0.16919,0.14387],"tcp_start":[0.61471,0.15733,0.31709],"tcp_to_object_dist_end":0.18744,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3959,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.05562,"descend_grasp.descend_z":0.01667,"descend_place.place_offset_z":-0.01611,"lift.lift_height":0.17103,"transport.arc_height":0.05688,"transport.transport_speed":0.05456},"optimized_scores":{"best_composite_score":0.12208,"best_fitness_score":0.54208,"best_task_score":0.16463},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1487.0,"contact_point_centroid":[0.50552,0.08279,-0.00274],"force_p95":0.3791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.10743,"mean_force":0.16521,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5242,0.11762,0.3618]},{"body_a":"world","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.48122,0.04646,-0.00166],"force_p95":0.342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37649,"mean_force":0.09878,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46977,0.04626,0.05015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5859.0,"contact_point_centroid":[0.47791,0.06509,0.1324],"force_p95":0.13904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33589,"mean_force":0.07673,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47488,0.04651,0.13184]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5482.0,"contact_point_centroid":[0.47805,0.02763,0.13318],"force_p95":0.14329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31511,"mean_force":0.07894,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47496,0.04652,0.1332]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04864,-0.0022],"force_p95":0.17973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23193,"mean_force":0.13705,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47199,0.04649,0.04983]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.49097,0.01944,0.23577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4147.0,"contact_point_centroid":[0.47098,0.02723,0.04948],"force_p95":0.08734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1276,"mean_force":0.05554,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47091,0.04638,0.0487]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47956,0.04384,0.11272]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.50452,0.08307,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5726,0.21256,0.30811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5124.0,"contact_point_centroid":[0.47095,0.0655,0.04958],"force_p95":0.07382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07695,"mean_force":0.04288,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47091,0.04639,0.04871]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1540.0,"contact_point_centroid":[0.52617,0.12037,0.36686],"force_p95":0.01161,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52562,0.12035,0.36454]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1110.0,"contact_point_centroid":[0.57317,0.21267,0.30972],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57263,0.21264,0.30753]}],"total_contact_groups":12},"final_pose_error":0.01955,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50452,0.08307,0.01602],"final_tcp_position":[0.57746,0.22352,0.23266],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273008.98032,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":22.6234,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48243,0.0408,0.16835],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47873,0.04712,0.05704],"tcp_start":[0.48243,0.0408,0.16835],"tcp_to_object_dist_end":0.03131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.04718,0.02519],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29151,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18076,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11071.0,"raw_peak_contact_force":0.23193,"tcp_end":[0.47088,0.04638,0.04867],"tcp_start":[0.47873,0.04712,0.05704],"tcp_to_object_dist_end":0.02632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":450.0,"n_steps_budget":930.0,"object_pos_end":[0.49292,0.04811,0.13993],"object_pos_start":[0.48273,0.04718,0.02519],"object_to_goal_dist_end":0.22086,"object_to_goal_dist_start":0.29151,"object_z_max":0.21682,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11410.0,"raw_peak_contact_force":0.37649,"tcp_end":[0.48871,0.04766,0.28147],"tcp_start":[0.47784,0.0467,0.16702],"tcp_to_object_dist_end":0.14161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.50452,0.08307,0.01602],"object_pos_start":[0.5083,0.06534,0.16539],"object_to_goal_dist_end":0.27061,"object_to_goal_dist_start":0.19075,"object_z_max":0.16539,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3027.0,"raw_peak_contact_force":2.10743,"subtask_id":"reach_goal","tcp_end":[0.56829,0.20223,0.38201],"tcp_start":[0.48871,0.04766,0.28147],"tcp_to_object_dist_end":0.39015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50452,0.08307,0.01602],"object_pos_start":[0.50452,0.08307,0.01602],"object_to_goal_dist_end":0.27061,"object_to_goal_dist_start":0.27061,"object_z_max":0.01602,"peak_contact_force":273008.98032,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2158.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57746,0.22352,0.23266],"tcp_start":[0.56829,0.20223,0.38201],"tcp_to_object_dist_end":0.26828,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56458,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_obj.approach_speed":0.08635,"descend_grasp.descend_z":0.01567,"descend_place.place_offset_z":0.01627,"lift.lift_height":0.19118,"transport.arc_height":0.05326,"transport.transport_speed":0.05972},"optimized_scores":{"best_composite_score":0.10942,"best_fitness_score":0.52942,"best_task_score":0.13255},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":469.0,"contact_point_centroid":[0.56475,-0.00587,-0.00427],"force_p95":0.96282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9863,"mean_force":0.23516,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54021,-0.02059,0.26349]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5141.0,"contact_point_centroid":[0.52975,-0.0017,0.11943],"force_p95":0.12589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27284,"mean_force":0.07584,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52576,-0.02059,0.11712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5181.0,"contact_point_centroid":[0.52919,-0.03949,0.1168],"force_p95":0.12809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27249,"mean_force":0.07608,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52558,-0.02058,0.11488]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02126,-0.00207],"force_p95":0.14274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18944,"mean_force":0.12816,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52398,-0.02059,0.0464]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51301,-0.00861,0.23484]},{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.56941,-0.00371,-0.00199],"force_p95":0.12349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13365,"mean_force":0.12281,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57162,0.07876,0.36852]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52853,-0.01929,0.11102]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.56941,-0.00371,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60466,0.21041,0.30418]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.52399,-0.00132,0.04756],"force_p95":0.06919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10243,"mean_force":0.04506,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52279,-0.02056,0.04502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5402.0,"contact_point_centroid":[0.52341,-0.03978,0.0476],"force_p95":0.06583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08059,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52279,-0.02056,0.04502]},{"body_a":"left_finger","body_b":"right_finger","contact_count":242.0,"contact_point_centroid":[0.54485,-0.0206,0.3132],"force_p95":0.01462,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01158,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54467,-0.02059,0.31083]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1955.0,"contact_point_centroid":[0.57188,0.07833,0.3707],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01042,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57151,0.07833,0.36844]},{"body_a":"left_finger","body_b":"right_finger","contact_count":899.0,"contact_point_centroid":[0.60495,0.2104,0.30677],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60465,0.21039,0.30432]}],"total_contact_groups":13},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.56941,-0.00371,0.01602],"final_tcp_position":[0.60676,0.22134,0.24228],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273003.91847,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.528,-0.01793,0.16727],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53128,-0.02071,0.05514],"tcp_start":[0.528,-0.01793,0.16727],"tcp_to_object_dist_end":0.02968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02079,0.02573],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14111,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12038.0,"raw_peak_contact_force":0.18944,"tcp_end":[0.52276,-0.02056,0.04498],"tcp_start":[0.53128,-0.02071,0.05514],"tcp_to_object_dist_end":0.02392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.55031,-0.02057,0.16425],"object_pos_start":[0.53696,-0.02079,0.02573],"object_to_goal_dist_end":0.25909,"object_to_goal_dist_start":0.31649,"object_z_max":0.19275,"peak_contact_force":273003.91847,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11033.0,"raw_peak_contact_force":1.9863,"tcp_end":[0.54653,-0.02059,0.32599],"tcp_start":[0.53189,-0.02069,0.18769],"tcp_to_object_dist_end":0.16178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.56941,-0.00371,0.01602],"object_pos_start":[0.5694,-0.00345,0.01636],"object_to_goal_dist_end":0.30312,"object_to_goal_dist_start":0.30271,"object_z_max":0.01636,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3783.0,"raw_peak_contact_force":0.13365,"subtask_id":"reach_goal","tcp_end":[0.603,0.20004,0.36459],"tcp_start":[0.54653,-0.02059,0.32599],"tcp_to_object_dist_end":0.40515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.56941,-0.00371,0.01602],"object_pos_start":[0.56941,-0.00371,0.01602],"object_to_goal_dist_end":0.30312,"object_to_goal_dist_start":0.30312,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1739.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.60676,0.22134,0.24228],"tcp_start":[0.603,0.20004,0.36459],"tcp_to_object_dist_end":0.3213,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```