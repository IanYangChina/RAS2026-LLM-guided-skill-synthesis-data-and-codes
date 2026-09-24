## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1288 | 0.46 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0774 | 0.47 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1243 | 0.45 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2455 | 0.46 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2493 | 0.46 | ❌ rejected |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
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
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b

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
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605988) | final destination targets |
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

## Current Skill (Q=0.129) — your mutation base

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
- id: grasp_object
  anchor: object
  target_entity: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: transport_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.3
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
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
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp_1
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
  subtask_id: grasp_object
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
  subtask_id: lift_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
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
  subtask_id: transport_to_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_1
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
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
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
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.129
- **task_score** (E): 0.462
- **fitness_score**: 0.709  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1574 |
| descend_1 | 1.00 | 1.00 | 0.1141 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1731 |
| transport_1 | 1.00 | 1.00 | 0.2360 |
| descend_2 | 1.00 | 1.00 | 0.1520 |
| release_1 | 1.00 | 1.00 | 0.0194 |
| retract_1 | 1.00 | 1.00 | 0.0938 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.506, 0.002, 0.034) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.034)→(0.497, 0.001, 0.026) | (0.511, 0.002, 0.026)→(0.511, 0.001, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.140 | 0.198 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.001, 0.026)→(0.507, 0.001, 0.198) | (0.511, 0.001, 0.026)→(0.518, 0.002, 0.193) | 0.246→0.219 | 1.00 / 38.000 | 0.080 | 0.586 |
| transport_1 | approach | 1.00 / step_budget | (0.507, 0.001, 0.198)→(0.619, 0.172, 0.308) | (0.518, 0.002, 0.193)→(0.629, 0.172, 0.296) | 0.219→0.159 | 1.00 / 34.333 | 0.084 | 0.109 |
| descend_2 | descend | 1.00 / step_budget | (0.619, 0.172, 0.308)→(0.622, 0.179, 0.157) | (0.629, 0.172, 0.296)→(0.623, 0.178, 0.141) | 0.159→0.009 | 1.00 / 33.333 | 0.099 | 0.181 |
| release_1 | release | 1.00 / step_budget | (0.622, 0.179, 0.157)→(0.615, 0.177, 0.175) | (0.623, 0.178, 0.141)→(0.617, 0.179, 0.017) | 0.009→0.123 | 1.00 / 4.000 | 0.151 | 1.490 |
| retract_1 | retract | 1.00 / step_budget | (0.615, 0.177, 0.175)→(0.623, 0.180, 0.268) | (0.617, 0.179, 0.017)→(0.616, 0.181, 0.019) | 0.123→0.121 | 1.00 / 4.000 | 0.123 | 0.157 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.554
- phase_score: 0.543
- phase_breakdown.place_at_goal_score: 0.073
- phase_breakdown.transport_to_goal_score: 0.746
- phase_breakdown.reach_object_score: 0.673
- phase_breakdown.grasp_object_score: 0.748
- phase_breakdown.lift_object_score: 0.883
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.554
- **Median Q (composite search score)**: 0.160
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.275


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `952d4e9e12c194d228cf63d10b31c959edc327920598c352d26dcf1284463776`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab36b663de63a40a5839be0af4fc1d53d37f9e78d4183a3de7f11063534632b8`; realized-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06473,"average_solve_count":448.0,"average_success_count":448.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05337,"descend_1.speed":0.04889,"descend_2.speed":0.08293,"lift_1.lift_height":0.19563,"lift_1.speed":0.03004,"retract_1.speed":0.05213,"transport_1.speed":0.03562,"transport_1.transport_height":0.18533},"optimized_scores":{"best_composite_score":0.16,"best_fitness_score":0.74,"best_task_score":0.51974},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":258.0,"contact_point_centroid":[0.62527,0.20478,-0.0049],"force_p95":1.01997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38281,"mean_force":0.29275,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61789,0.20256,0.14037]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.45505,-0.0256,-0.00148],"force_p95":0.61908,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64494,"mean_force":0.2886,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4459,-0.02564,0.02234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12196.0,"contact_point_centroid":[0.44903,-0.04466,0.11301],"force_p95":0.07422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24679,"mean_force":0.05109,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44887,-0.02552,0.11112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12018.0,"contact_point_centroid":[0.44898,-0.00638,0.11198],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2429,"mean_force":0.05151,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44879,-0.02552,0.10995]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02613,-0.00205],"force_p95":0.13813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19146,"mean_force":0.12702,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44791,-0.02571,0.02252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5656.0,"contact_point_centroid":[0.62209,0.21987,0.21175],"force_p95":0.0727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14728,"mean_force":0.04922,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62206,0.20081,0.20978]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48087,-0.01075,0.22638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1225.0,"contact_point_centroid":[0.62252,0.18501,0.12905],"force_p95":0.07304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13762,"mean_force":0.04345,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62228,0.20423,0.12691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1259.0,"contact_point_centroid":[0.62243,0.22347,0.12873],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13231,"mean_force":0.04239,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62226,0.20422,0.12686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5483.0,"contact_point_centroid":[0.62208,0.18161,0.21021],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13016,"mean_force":0.05047,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62211,0.20089,0.20796]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.62974,0.20468,-0.00198],"force_p95":0.12338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12513,"mean_force":0.12232,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62082,0.20415,0.19682]},{"body_a":"world","body_b":"grasp_target","contact_count":3000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45618,-0.02418,0.08603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17936.0,"contact_point_centroid":[0.54052,0.11052,0.24682],"force_p95":0.07638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09322,"mean_force":0.05293,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54013,0.09133,0.24456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.44682,-0.00647,0.02383],"force_p95":0.06768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09243,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44681,-0.02567,0.02149]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20033.0,"contact_point_centroid":[0.53735,0.0684,0.24488],"force_p95":0.07102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08769,"mean_force":0.04832,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5372,0.08745,0.24303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44667,-0.04491,0.02332],"force_p95":0.06644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08655,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44682,-0.02567,0.02149]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62974,0.20468,0.01602],"final_tcp_position":[0.62632,0.2066,0.24456],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46142,-0.02246,0.14925],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.4543,-0.02594,0.02852],"tcp_start":[0.46142,-0.02246,0.14925],"tcp_to_object_dist_end":0.00496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02566,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13549,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11783.0,"raw_peak_contact_force":0.19146,"subtask_id":"grasp_object","tcp_end":[0.44679,-0.02567,0.02147],"tcp_start":[0.4543,-0.02594,0.02852],"tcp_to_object_dist_end":0.01242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.4656,-0.02533,0.20236],"object_pos_start":[0.45842,-0.02566,0.02582],"object_to_goal_dist_end":0.299,"object_to_goal_dist_start":0.30328,"object_z_max":0.20208,"peak_contact_force":0.07863,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24301.0,"raw_peak_contact_force":0.64494,"subtask_id":"lift_object","tcp_end":[0.45445,-0.02552,0.20194],"tcp_start":[0.44679,-0.02567,0.02147],"tcp_to_object_dist_end":0.01116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.63036,0.19709,0.27832],"object_pos_start":[0.4656,-0.02533,0.20236],"object_to_goal_dist_end":0.16458,"object_to_goal_dist_start":0.299,"object_z_max":0.27827,"peak_contact_force":0.07344,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37969.0,"raw_peak_contact_force":0.09322,"subtask_id":"transport_to_goal","tcp_end":[0.62037,0.1971,0.28634],"tcp_start":[0.45445,-0.02552,0.20194],"tcp_to_object_dist_end":0.01281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.62432,0.20455,0.1225],"object_pos_start":[0.63036,0.19709,0.27832],"object_to_goal_dist_end":0.01083,"object_to_goal_dist_start":0.16458,"object_z_max":0.27832,"peak_contact_force":0.06905,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11139.0,"raw_peak_contact_force":0.14728,"subtask_id":"place_at_goal","tcp_end":[0.62491,0.20506,0.13267],"tcp_start":[0.62037,0.1971,0.28634],"tcp_to_object_dist_end":0.0102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62997,0.20461,0.01613],"object_pos_start":[0.62432,0.20455,0.1225],"object_to_goal_dist_end":0.09805,"object_to_goal_dist_start":0.01083,"object_z_max":0.1225,"peak_contact_force":0.11416,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2742.0,"raw_peak_contact_force":1.38281,"subtask_id":"place_at_goal","tcp_end":[0.61781,0.20253,0.1503],"tcp_start":[0.62491,0.20506,0.13267],"tcp_to_object_dist_end":0.13474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.62974,0.20468,0.01602],"object_pos_start":[0.62997,0.20461,0.01613],"object_to_goal_dist_end":0.09816,"object_to_goal_dist_start":0.09805,"object_z_max":0.01635,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.12513,"subtask_id":"place_at_goal","tcp_end":[0.62632,0.2066,0.24456],"tcp_start":[0.61781,0.20253,0.1503],"tcp_to_object_dist_end":0.22857,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22997,"average_solve_count":387.0,"average_success_count":387.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07319,"descend_1.speed":0.09211,"descend_2.speed":0.0566,"lift_1.lift_height":0.21021,"lift_1.speed":0.02833,"retract_1.speed":0.07539,"transport_1.speed":0.05605,"transport_1.transport_height":0.20033},"optimized_scores":{"best_composite_score":0.0521,"best_fitness_score":0.6321,"best_task_score":0.31108},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.64731,0.16359,-0.0081],"force_p95":1.3592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82158,"mean_force":0.49589,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63855,0.15442,0.22177]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.54015,0.00072,-0.00148],"force_p95":0.52215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55887,"mean_force":0.21799,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52839,0.00083,0.02761]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":587.0,"contact_point_centroid":[0.64502,0.13739,0.19997],"force_p95":0.16314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41364,"mean_force":0.10345,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6417,0.15543,0.20416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13235.0,"contact_point_centroid":[0.53351,-0.01837,0.12403],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26735,"mean_force":0.05602,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53268,0.00073,0.12169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":613.0,"contact_point_centroid":[0.64428,0.17368,0.1999],"force_p95":0.19316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26657,"mean_force":0.10124,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64161,0.15541,0.204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2849.0,"contact_point_centroid":[0.64603,0.17119,0.29554],"force_p95":0.16054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26237,"mean_force":0.10073,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64261,0.15285,0.29833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13639.0,"contact_point_centroid":[0.53321,0.01979,0.12047],"force_p95":0.07793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25856,"mean_force":0.05484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53244,0.00073,0.1183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2937.0,"contact_point_centroid":[0.64655,0.13452,0.29909],"force_p95":0.14795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24958,"mean_force":0.09861,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.64257,0.15276,0.30132]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15901,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53071,0.00088,0.02829]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.64887,0.16299,-0.00205],"force_p95":0.12648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15543,"mean_force":0.11954,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.64076,0.15548,0.27396]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15455.0,"contact_point_centroid":[0.59085,0.05577,0.29279],"force_p95":0.08483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13947,"mean_force":0.05813,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58876,0.07459,0.29191]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13805.0,"contact_point_centroid":[0.59128,0.09411,0.29368],"force_p95":0.09171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13897,"mean_force":0.06434,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5891,0.0751,0.29245]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51604,0.00044,0.22502]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53517,0.00096,0.07907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53061,-0.01834,0.02952],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11315,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52946,0.00086,0.02684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53053,0.01994,0.02864],"force_p95":0.06812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09627,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52946,0.00086,0.02684]}],"total_contact_groups":16},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64887,0.16297,0.01602],"final_tcp_position":[0.64505,0.1571,0.32138],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.82158,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53474,0.00093,0.14754],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53786,0.00101,0.03658],"tcp_start":[0.53474,0.00093,0.14754],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12987,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15901,"subtask_id":"grasp_object","tcp_end":[0.52943,0.00086,0.02681],"tcp_start":[0.53786,0.00101,0.03658],"tcp_to_object_dist_end":0.01477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.5519,0.0007,0.20886],"object_pos_start":[0.54416,0.00073,0.02588],"object_to_goal_dist_end":0.18506,"object_to_goal_dist_start":0.25053,"object_z_max":0.20861,"peak_contact_force":0.08141,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26968.0,"raw_peak_contact_force":0.55887,"subtask_id":"lift_object","tcp_end":[0.53999,0.00068,0.21674],"tcp_start":[0.52943,0.00086,0.02681],"tcp_to_object_dist_end":0.01428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":908.0,"n_steps_budget":1000.0,"object_pos_end":[0.65501,0.15066,0.35806],"object_pos_start":[0.5519,0.0007,0.20886],"object_to_goal_dist_end":0.16729,"object_to_goal_dist_start":0.18506,"object_z_max":0.35794,"peak_contact_force":0.10838,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29260.0,"raw_peak_contact_force":0.13947,"subtask_id":"transport_to_goal","tcp_end":[0.64156,0.15031,0.37412],"tcp_start":[0.53999,0.00068,0.21674],"tcp_to_object_dist_end":0.02095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.65161,0.15577,0.18861],"object_pos_start":[0.65501,0.15066,0.35806],"object_to_goal_dist_end":0.00524,"object_to_goal_dist_start":0.16729,"object_z_max":0.35806,"peak_contact_force":0.15281,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5786.0,"raw_peak_contact_force":0.26237,"subtask_id":"place_at_goal","tcp_end":[0.64395,0.15601,0.21033],"tcp_start":[0.64156,0.15031,0.37412],"tcp_to_object_dist_end":0.02303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64839,0.1588,0.00833],"object_pos_start":[0.65161,0.15577,0.18861],"object_to_goal_dist_end":0.18278,"object_to_goal_dist_start":0.00524,"object_z_max":0.18861,"peak_contact_force":0.16578,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1352.0,"raw_peak_contact_force":1.82158,"subtask_id":"place_at_goal","tcp_end":[0.63852,0.15441,0.22772],"tcp_start":[0.64395,0.15601,0.21033],"tcp_to_object_dist_end":0.21966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":960.0,"object_pos_end":[0.64887,0.16297,0.01602],"object_pos_start":[0.64839,0.1588,0.00833],"object_to_goal_dist_end":0.17516,"object_to_goal_dist_start":0.18278,"object_z_max":0.01677,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.15543,"subtask_id":"place_at_goal","tcp_end":[0.64505,0.1571,0.32138],"tcp_start":[0.63852,0.15441,0.22772],"tcp_to_object_dist_end":0.30545,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32641,"average_solve_count":337.0,"average_success_count":337.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07822,"descend_1.speed":0.07659,"descend_2.speed":0.09688,"lift_1.lift_height":0.17026,"lift_1.speed":0.03709,"retract_1.speed":0.06529,"transport_1.speed":0.04083,"transport_1.transport_height":0.17164},"optimized_scores":{"best_composite_score":0.17418,"best_fitness_score":0.75418,"best_task_score":0.55443},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":241.0,"contact_point_centroid":[0.57501,0.17244,-0.00509],"force_p95":0.98636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26486,"mean_force":0.29228,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5894,0.17329,0.13445]},{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.52649,0.02877,-0.00155],"force_p95":0.52945,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55548,"mean_force":0.20159,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51515,0.02919,0.0293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10965.0,"contact_point_centroid":[0.51918,0.04809,0.10057],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27666,"mean_force":0.05333,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51874,0.02903,0.0985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10083.0,"contact_point_centroid":[0.51952,0.00989,0.10352],"force_p95":0.08309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26631,"mean_force":0.05645,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51896,0.02903,0.10091]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03048,-0.00214],"force_p95":0.16345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24419,"mean_force":0.13342,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51742,0.02935,0.02967]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.56873,0.17478,-0.00198],"force_p95":0.15551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1904,"mean_force":0.12304,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59205,0.17477,0.19199]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1215.0,"contact_point_centroid":[0.59408,0.15561,0.12391],"force_p95":0.07423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17197,"mean_force":0.0447,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59376,0.17475,0.12177]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1238.0,"contact_point_centroid":[0.59402,0.19399,0.12334],"force_p95":0.07302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16246,"mean_force":0.04402,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59374,0.17474,0.12173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.51717,0.01007,0.03103],"force_p95":0.08118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14812,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51619,0.02927,0.02829]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5103,0.01267,0.22501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.59479,0.19042,0.20018],"force_p95":0.07512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13243,"mean_force":0.05027,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59473,0.17139,0.19852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4886.0,"contact_point_centroid":[0.59485,0.15217,0.19878],"force_p95":0.07831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1266,"mean_force":0.05152,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59475,0.17147,0.19667]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52245,0.02842,0.07748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13492.0,"contact_point_centroid":[0.56016,0.08207,0.22151],"force_p95":0.07057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09406,"mean_force":0.04768,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55974,0.10116,0.22009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5009.0,"contact_point_centroid":[0.51709,0.04844,0.03008],"force_p95":0.07379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08595,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51619,0.02927,0.0283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12432.0,"contact_point_centroid":[0.56144,0.12281,0.22319],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08581,"mean_force":0.05131,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.561,0.10363,0.22173]}],"total_contact_groups":16},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56871,0.17478,0.02602],"final_tcp_position":[0.5974,0.17703,0.23873],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.26486,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52282,0.0263,0.14771],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52438,0.02982,0.03754],"tcp_start":[0.52282,0.0263,0.14771],"tcp_to_object_dist_end":0.01308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02931,0.02554],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15482,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10866.0,"raw_peak_contact_force":0.24419,"subtask_id":"grasp_object","tcp_end":[0.51616,0.02927,0.02826],"tcp_start":[0.52438,0.02982,0.03754],"tcp_to_object_dist_end":0.0145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.53743,0.02917,0.16882],"object_pos_start":[0.5304,0.02931,0.02554],"object_to_goal_dist_end":0.17356,"object_to_goal_dist_start":0.18481,"object_z_max":0.16857,"peak_contact_force":0.07994,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21145.0,"raw_peak_contact_force":0.55548,"subtask_id":"lift_object","tcp_end":[0.52566,0.02907,0.17645],"tcp_start":[0.51616,0.02927,0.02826],"tcp_to_object_dist_end":0.01403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.60304,0.16782,0.25181],"object_pos_start":[0.53743,0.02917,0.16882],"object_to_goal_dist_end":0.14413,"object_to_goal_dist_start":0.17356,"object_z_max":0.25169,"peak_contact_force":0.06883,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25924.0,"raw_peak_contact_force":0.09406,"subtask_id":"transport_to_goal","tcp_end":[0.59402,0.16789,0.26477],"tcp_start":[0.52566,0.02907,0.17645],"tcp_to_object_dist_end":0.01579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.5924,0.17484,0.11233],"object_pos_start":[0.60304,0.16782,0.25181],"object_to_goal_dist_end":0.01075,"object_to_goal_dist_start":0.14413,"object_z_max":0.25183,"peak_contact_force":0.07654,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9954.0,"raw_peak_contact_force":0.13243,"subtask_id":"place_at_goal","tcp_end":[0.59647,0.17549,0.12699],"tcp_start":[0.59402,0.16789,0.26477],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57149,0.17367,0.02649],"object_pos_start":[0.5924,0.17484,0.11233],"object_to_goal_dist_end":0.08709,"object_to_goal_dist_start":0.01075,"object_z_max":0.11233,"peak_contact_force":0.17161,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2694.0,"raw_peak_contact_force":1.26486,"subtask_id":"place_at_goal","tcp_end":[0.58929,0.17325,0.14628],"tcp_start":[0.59647,0.17549,0.12699],"tcp_to_object_dist_end":0.12111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.56871,0.17478,0.02602],"object_pos_start":[0.57149,0.17367,0.02649],"object_to_goal_dist_end":0.08847,"object_to_goal_dist_start":0.08709,"object_z_max":0.02649,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.1904,"subtask_id":"place_at_goal","tcp_end":[0.5974,0.17703,0.23873],"tcp_start":[0.58929,0.17325,0.14628],"tcp_to_object_dist_end":0.21465,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```