## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.1381 | 0.22 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | -0.2492 | 0.18 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | -0.2148 | 0.20 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2851 | 0.27 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2595 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.138) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach_1
- id: descend_1
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: descend_1
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
  subtask_id: grasp_1
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
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: transport_arc
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
- id: release_1
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
  subtask_id: release_1
- id: retract_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.138
- **task_score** (E): 0.218
- **fitness_score**: 0.342  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1714 |
| descend_1 | 0.33 | 1.00 | 0.1271 |
| grasp_1 | 1.00 | 1.00 | 0.0046 |
| lift_1 | 1.00 | 1.00 | 0.0944 |
| transport_arc | 0.33 | 1.00 | 0.1060 |
| descend_place | 0.33 | 1.00 | 0.0143 |
| release_1 | 1.00 | 1.00 | 0.0188 |
| retract_1 | 0.67 | 1.00 | 0.0870 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.438, 0.003, 0.167) | (0.511, 0.002, 0.030)→(0.490, 0.002, 0.023) | 0.244→0.258 | 1.00 / 4.667 | 134.942 | 1046.557 |
| descend_1 | descend | 0.33 / step_budget | (0.438, 0.003, 0.167)→(0.475, 0.002, 0.101) | (0.490, 0.002, 0.023)→(0.495, 0.002, 0.022) | 0.258→0.256 | 1.00 / 5.000 | 193.359 | 373.495 |
| grasp_1 | grasp | 1.00 / step_budget | (0.475, 0.002, 0.101)→(0.472, 0.002, 0.097) | (0.495, 0.002, 0.022)→(0.495, 0.002, 0.022) | 0.256→0.256 | 1.00 / 22.667 | 43.992 | 79.052 |
| lift_1 | lift | 1.00 / step_budget | (0.471, 0.002, 0.272)→(0.483, -0.002, 0.360) | (0.495, 0.002, 0.022)→(0.494, 0.002, 0.061) | 0.256→0.238 | 1.00 / 14.000 | 0.117 | 93.570 |
| transport_arc | approach | 0.33 / step_budget | (0.483, -0.002, 0.360)→(0.549, 0.073, 0.358) | (0.494, 0.002, 0.061)→(0.512, 0.023, 0.019) | 0.238→0.241 | 1.00 / 8.667 | 148.869 | 287.698 |
| descend_place | descend | 0.33 / step_budget | (0.549, 0.073, 0.358)→(0.555, 0.079, 0.350) | (0.512, 0.023, 0.019)→(0.512, 0.023, 0.019) | 0.241→0.241 | 1.00 / 8.667 | 106.195 | 150.912 |
| release_1 | release | 1.00 / step_budget | (0.555, 0.079, 0.350)→(0.555, 0.079, 0.368) | (0.512, 0.023, 0.019)→(0.512, 0.023, 0.019) | 0.241→0.241 | 1.00 / 4.333 | 24.160 | 104.424 |
| retract_1 | retract | 0.67 / step_budget | (0.555, 0.079, 0.368)→(0.555, 0.078, 0.455) | (0.512, 0.023, 0.019)→(0.512, 0.023, 0.019) | 0.241→0.241 | 1.00 / 4.333 | 67.848 | 92.315 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.253
- phase_score: 0.709
- phase_breakdown.release_1_score: 0.675
- phase_breakdown.descend_1_score: 0.866
- phase_breakdown.transport_arc_score: 0.674
- phase_breakdown.approach_1_score: 0.004
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.591

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.591
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.292
- **Median Q (composite search score)**: -0.206
- **K-run variance**: 0.0331
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.355


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":211.0,"average_failure_rate":0.62059,"average_mean_iterations":126.40588,"average_solve_count":340.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23565,"descend_1.grasp_z_offset":0.04996,"descend_place.descend_offset":0.03025,"lift_1.lift_height":0.17913,"release_1.release_force":4.45351,"transport_arc.arc_height":0.33114},"optimized_scores":{"best_composite_score":-0.31921,"best_fitness_score":0.16079,"best_task_score":0.10926},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":732.0,"contact_point_centroid":[0.61517,-0.01502,-0.00052],"force_p95":213.28409,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1620.99814,"mean_force":213.90622,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36479,-0.01205,0.09771]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.63761,-0.02068,-0.0003],"force_p95":342.41756,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":559.00973,"mean_force":304.24185,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39386,-0.02035,0.12127]},{"body_a":"link5","body_b":"hand","contact_count":159.0,"contact_point_centroid":[0.55259,0.04281,0.45135],"force_p95":182.40276,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.08972,"mean_force":123.36092,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49176,-0.0441,0.49057]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.65544,-0.02415,-0.0001],"force_p95":112.98653,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.63013,"mean_force":94.32403,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42368,-0.02287,0.14428]},{"body_a":"link5","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.55046,0.02816,0.42262],"force_p95":109.90514,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.72069,"mean_force":57.48348,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.49566,-0.0316,0.50451]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.65527,-0.0241,-0.00013],"force_p95":76.17432,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.00022,"mean_force":69.97101,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.42362,-0.02283,0.14441]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43899,-0.0252,0.04242],"force_p95":3.58945,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.01362,"mean_force":1.59718,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36898,-0.00794,0.05544]},{"body_a":"world","body_b":"grasp_target","contact_count":3311.0,"contact_point_centroid":[0.42316,-0.02685,-0.00215],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25584,"mean_force":0.14007,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38136,-0.01121,0.11165]},{"body_a":"grasp_target","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.46601,-0.01276,0.01087],"force_p95":0.53772,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58967,"mean_force":0.1903,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.35872,-0.00796,0.0562]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41713,-0.02696,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39386,-0.02035,0.12127]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41713,-0.02696,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.42362,-0.02283,0.14441]},{"body_a":"world","body_b":"grasp_target","contact_count":6900.0,"contact_point_centroid":[0.41713,-0.02696,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42802,-0.02483,0.38756]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.41713,-0.02696,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48851,-0.04288,0.49232]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.41713,-0.02696,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.49782,-0.03108,0.49714]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41713,-0.02696,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50235,-0.03097,0.49098]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.41713,-0.02696,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50355,-0.03073,0.51198]}],"total_contact_groups":22},"final_pose_error":0.14934,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41713,-0.02696,0.01602],"final_tcp_position":[0.50352,-0.03061,0.51242],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273003.62252,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.41713,-0.02696,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33211,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":211.91821,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4123.0,"raw_peak_contact_force":1620.99814,"subtask_id":"approach_1","tcp_end":[0.35965,-0.01772,0.09491],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09805,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41713,-0.02696,0.01602],"object_pos_start":[0.41713,-0.02696,0.01602],"object_to_goal_dist_end":0.33211,"object_to_goal_dist_start":0.33211,"object_z_max":0.01602,"peak_contact_force":285.44349,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":559.00973,"subtask_id":"descend_1","tcp_end":[0.4232,-0.02273,0.14491],"tcp_start":[0.35965,-0.01772,0.09491],"tcp_to_object_dist_end":0.12911,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41713,-0.02696,0.01602],"object_pos_start":[0.41713,-0.02696,0.01602],"object_to_goal_dist_end":0.33211,"object_to_goal_dist_start":0.33211,"object_z_max":0.01602,"peak_contact_force":67.57595,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3502.0,"raw_peak_contact_force":85.00022,"tcp_end":[0.42368,-0.02287,0.14426],"tcp_start":[0.42368,-0.02287,0.14426],"tcp_to_object_dist_end":0.12847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1725.0,"n_steps_budget":1000.0,"object_pos_end":[0.41713,-0.02696,0.01602],"object_pos_start":[0.41713,-0.02696,0.01602],"object_to_goal_dist_end":0.33211,"object_to_goal_dist_start":0.33211,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14222.0,"raw_peak_contact_force":116.63013,"tcp_end":[0.46295,-0.03486,0.50334],"tcp_start":[0.42435,-0.02415,0.46813],"tcp_to_object_dist_end":0.48954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.41713,-0.02696,0.01602],"object_pos_start":[0.41713,-0.02696,0.01602],"object_to_goal_dist_end":0.33211,"object_to_goal_dist_start":0.33211,"object_z_max":0.01602,"peak_contact_force":117.66345,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1713.0,"raw_peak_contact_force":374.08972,"subtask_id":"transport_arc","tcp_end":[0.49565,-0.03167,0.50457],"tcp_start":[0.46295,-0.03486,0.50334],"tcp_to_object_dist_end":0.49484,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.41713,-0.02696,0.01602],"object_pos_start":[0.41713,-0.02696,0.01602],"object_to_goal_dist_end":0.33211,"object_to_goal_dist_start":0.33211,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":459.0,"raw_peak_contact_force":110.72069,"tcp_end":[0.50002,-0.03095,0.48889],"tcp_start":[0.49565,-0.03167,0.50457],"tcp_to_object_dist_end":0.4801,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41713,-0.02696,0.01602],"object_pos_start":[0.41713,-0.02696,0.01602],"object_to_goal_dist_end":0.33211,"object_to_goal_dist_start":0.33211,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.50358,-0.03077,0.51176],"tcp_start":[0.50002,-0.03095,0.48889],"tcp_to_object_dist_end":0.50324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":960.0,"object_pos_end":[0.41713,-0.02696,0.01602],"object_pos_start":[0.41713,-0.02696,0.01602],"object_to_goal_dist_end":0.33211,"object_to_goal_dist_start":0.33211,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50352,-0.03061,0.51242],"tcp_start":[0.50358,-0.03077,0.51176],"tcp_to_object_dist_end":0.50388,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2732,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25177,"descend_1.grasp_z_offset":0.02052,"descend_place.descend_offset":0.00888,"lift_1.lift_height":0.1396,"release_1.release_force":5.30963,"transport_arc.arc_height":0.30775},"optimized_scores":{"best_composite_score":0.11054,"best_fitness_score":0.59054,"best_task_score":0.25272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1115.0,"contact_point_centroid":[0.59419,0.06239,-0.00292],"force_p95":0.50481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63459,"mean_force":0.17201,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60238,0.10217,0.20013]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54208,0.00061,-0.00133],"force_p95":0.39669,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41829,"mean_force":0.08292,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52927,0.00078,0.04607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7553.0,"contact_point_centroid":[0.52916,0.01979,0.10117],"force_p95":0.09106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28071,"mean_force":0.0591,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52669,0.00073,0.09858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7328.0,"contact_point_centroid":[0.52924,-0.01833,0.1012],"force_p95":0.0974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26749,"mean_force":0.06042,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52665,0.00072,0.09873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2361.0,"contact_point_centroid":[0.54618,0.00217,0.17804],"force_p95":0.125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22007,"mean_force":0.07999,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53984,0.02077,0.17816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2215.0,"contact_point_centroid":[0.54592,0.03875,0.17897],"force_p95":0.11527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21738,"mean_force":0.08212,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53936,0.02009,0.17773]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00105,-0.00204],"force_p95":0.13361,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1672,"mean_force":0.12599,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53191,0.00084,0.04618]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.54431,0.00113,-0.00101],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12135,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51745,0.00039,0.30348]},{"body_a":"world","body_b":"grasp_target","contact_count":3196.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13511,"mean_force":0.12283,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54065,0.0008,0.17562]},{"body_a":"world","body_b":"grasp_target","contact_count":2676.0,"contact_point_centroid":[0.59433,0.06283,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63947,0.15174,0.18747]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59433,0.06283,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63975,0.15534,0.18924]},{"body_a":"world","body_b":"grasp_target","contact_count":2160.0,"contact_point_centroid":[0.59433,0.06283,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63652,0.15429,0.27235]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5090.0,"contact_point_centroid":[0.53105,-0.0185,0.04827],"force_p95":0.06529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09466,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53064,0.00081,0.04466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5854.0,"contact_point_centroid":[0.53092,0.02004,0.04747],"force_p95":0.06012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08079,"mean_force":0.03803,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53064,0.00081,0.04466]},{"body_a":"left_finger","body_b":"right_finger","contact_count":967.0,"contact_point_centroid":[0.60913,0.10967,0.20205],"force_p95":0.0128,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01068,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60828,0.10966,0.19991]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2890.0,"contact_point_centroid":[0.64041,0.15175,0.18959],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01033,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63947,0.15173,0.18747]}],"total_contact_groups":17},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.59433,0.06283,0.01602],"final_tcp_position":[0.63749,0.15447,0.33819],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.63459,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":34.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02629],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.24994,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.1356,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":132.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.54602,0.00077,0.30152],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":799.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02629],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24994,"object_z_max":0.02629,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3196.0,"raw_peak_contact_force":0.13511,"subtask_id":"descend_1","tcp_end":[0.53947,0.001,0.05534],"tcp_start":[0.54602,0.00077,0.30152],"tcp_to_object_dist_end":0.02971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00079,0.02583],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13226,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12744.0,"raw_peak_contact_force":0.1672,"tcp_end":[0.53061,0.00081,0.04462],"tcp_start":[0.53947,0.001,0.05534],"tcp_to_object_dist_end":0.0232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":408.0,"n_steps_budget":870.0,"object_pos_end":[0.54088,0.00064,0.14029],"object_pos_start":[0.54422,0.00079,0.02583],"object_to_goal_dist_end":0.19689,"object_to_goal_dist_start":0.25049,"object_z_max":0.14004,"peak_contact_force":0.10634,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14962.0,"raw_peak_contact_force":0.41829,"tcp_end":[0.52681,0.00072,0.16471],"tcp_start":[0.53061,0.00081,0.04462],"tcp_to_object_dist_end":0.02819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.59433,0.06283,0.01602],"object_pos_start":[0.54088,0.00064,0.14029],"object_to_goal_dist_end":0.20632,"object_to_goal_dist_start":0.19689,"object_z_max":0.16204,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6658.0,"raw_peak_contact_force":1.63459,"subtask_id":"transport_arc","tcp_end":[0.63466,0.14322,0.19033],"tcp_start":[0.52681,0.00072,0.16471],"tcp_to_object_dist_end":0.19615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.59433,0.06283,0.01602],"object_pos_start":[0.59433,0.06283,0.01602],"object_to_goal_dist_end":0.20632,"object_to_goal_dist_start":0.20632,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5566.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64347,0.15639,0.18984],"tcp_start":[0.63466,0.14322,0.19033],"tcp_to_object_dist_end":0.20343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59433,0.06283,0.01602],"object_pos_start":[0.59433,0.06283,0.01602],"object_to_goal_dist_end":0.20632,"object_to_goal_dist_start":0.20632,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63835,0.1549,0.20815],"tcp_start":[0.64347,0.15639,0.18984],"tcp_to_object_dist_end":0.21755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":930.0,"object_pos_end":[0.59433,0.06283,0.01602],"object_pos_start":[0.59433,0.06283,0.01602],"object_to_goal_dist_end":0.20632,"object_to_goal_dist_start":0.20632,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2160.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63749,0.15447,0.33819],"tcp_start":[0.63835,0.1549,0.20815],"tcp_to_object_dist_end":0.33772,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":118.0,"average_failure_rate":0.4403,"average_mean_iterations":90.92164,"average_solve_count":268.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27042,"descend_1.grasp_z_offset":0.03286,"descend_place.descend_offset":0.02754,"lift_1.lift_height":0.10959,"release_1.release_force":6.21049,"transport_arc.arc_height":0.31987},"optimized_scores":{"best_composite_score":-0.20572,"best_fitness_score":0.27428,"best_task_score":0.29171},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":89.0,"contact_point_centroid":[0.64968,0.02628,-0.00227],"force_p95":665.22892,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1518.53579,"mean_force":267.7602,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40142,0.02431,0.08475]},{"body_a":"world","body_b":"link6","contact_count":541.0,"contact_point_centroid":[0.68539,0.02951,-0.00018],"force_p95":316.99704,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.33909,"mean_force":284.52297,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.437,0.02662,0.11289]},{"body_a":"link5","body_b":"hand","contact_count":44.0,"contact_point_centroid":[0.55225,0.02781,0.36755],"force_p95":481.5403,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.37077,"mean_force":368.9747,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51387,0.10594,0.38178]},{"body_a":"link5","body_b":"hand","contact_count":20.0,"contact_point_centroid":[0.55317,0.03396,0.3421],"force_p95":338.9841,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.89318,"mean_force":314.88879,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51882,0.11004,0.37697]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.55283,0.0367,0.32335],"force_p95":282.72011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.02814,"mean_force":185.91551,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52305,0.11256,0.36537]},{"body_a":"link5","body_b":"hand","contact_count":489.0,"contact_point_centroid":[0.54959,0.03455,0.3964],"force_p95":264.34032,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.70047,"mean_force":207.51761,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52466,0.11103,0.4511]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.70553,0.02657,-0.0001],"force_p95":161.43845,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.66152,"mean_force":113.39654,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46137,0.0282,0.10305]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.70545,0.02662,-0.00012],"force_p95":72.2382,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.98959,"mean_force":66.85566,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46138,0.02823,0.10323]},{"body_a":"grasp_target","body_b":"link7","contact_count":102.0,"contact_point_centroid":[0.51704,0.02386,0.02989],"force_p95":4.4839,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.3826,"mean_force":1.22203,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40378,0.02426,0.08096]},{"body_a":"grasp_target","body_b":"hand","contact_count":102.0,"contact_point_centroid":[0.50916,0.01936,0.04719],"force_p95":2.77118,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.83528,"mean_force":0.97044,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40378,0.02426,0.08096]},{"body_a":"world","body_b":"grasp_target","contact_count":646.0,"contact_point_centroid":[0.52642,0.03066,-0.00363],"force_p95":1.14602,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16843,"mean_force":0.30275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47589,0.01831,0.16777]},{"body_a":"grasp_target","body_b":"hand","contact_count":543.0,"contact_point_centroid":[0.5207,0.0187,0.05903],"force_p95":0.30794,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.84026,"mean_force":0.14793,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43707,0.02663,0.11288]},{"body_a":"grasp_target","body_b":"link7","contact_count":194.0,"contact_point_centroid":[0.52124,0.02364,0.04089],"force_p95":0.48343,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.82414,"mean_force":0.20699,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42081,0.0257,0.11409]},{"body_a":"world","body_b":"grasp_target","contact_count":1198.0,"contact_point_centroid":[0.5144,0.03116,-0.00451],"force_p95":0.37552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42805,"mean_force":0.2801,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43914,0.02676,0.1123]},{"body_a":"grasp_target","body_b":"hand","contact_count":20.0,"contact_point_centroid":[0.54134,0.04089,0.05536],"force_p95":0.28292,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41158,"mean_force":0.09704,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46115,0.02817,0.10469]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.52594,0.03197,-0.00237],"force_p95":0.19904,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23949,"mean_force":0.14722,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46138,0.02823,0.10323]}],"total_contact_groups":28},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5247,0.03191,0.02602],"final_tcp_position":[0.52472,0.11042,0.51493],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273007.77414,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.50969,0.0313,0.02589],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19206,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":192.77201,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":958.0,"raw_peak_contact_force":1518.53579,"subtask_id":"approach_1","tcp_end":[0.40736,0.02517,0.10477],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12935,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.52386,0.03147,0.02513],"object_pos_start":[0.50969,0.0313,0.02589],"object_to_goal_dist_end":0.18589,"object_to_goal_dist_start":0.19206,"object_z_max":0.02638,"peak_contact_force":294.5097,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2476.0,"raw_peak_contact_force":561.33909,"subtask_id":"descend_1","tcp_end":[0.46123,0.02823,0.10386],"tcp_start":[0.40736,0.02517,0.10477],"tcp_to_object_dist_end":0.10065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.52394,0.03164,0.02522],"object_pos_start":[0.52386,0.03147,0.02513],"object_to_goal_dist_end":0.18569,"object_to_goal_dist_start":0.18589,"object_z_max":0.02523,"peak_contact_force":64.26759,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4076.0,"raw_peak_contact_force":151.98959,"tcp_end":[0.46142,0.02819,0.10307],"tcp_start":[0.46142,0.0282,0.10307],"tcp_to_object_dist_end":0.09991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":978.0,"n_steps_budget":690.0,"object_pos_end":[0.5247,0.03191,0.02602],"object_pos_start":[0.52374,0.03166,0.02523],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18575,"object_z_max":0.02604,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8156.0,"raw_peak_contact_force":163.66152,"tcp_end":[0.45957,0.02794,0.41258],"tcp_start":[0.45866,0.0279,0.30276],"tcp_to_object_dist_end":0.39203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.5247,0.03191,0.02602],"object_pos_start":[0.5247,0.03191,0.02602],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.1848,"object_z_max":0.02602,"peak_contact_force":328.81955,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3761.0,"raw_peak_contact_force":487.37077,"subtask_id":"transport_arc","tcp_end":[0.51768,0.10879,0.38052],"tcp_start":[0.45957,0.02794,0.41258],"tcp_to_object_dist_end":0.36281,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.5247,0.03191,0.02602],"object_pos_start":[0.5247,0.03191,0.02602],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.1848,"object_z_max":0.02602,"peak_contact_force":318.33875,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":188.0,"raw_peak_contact_force":341.89318,"tcp_end":[0.52038,0.11299,0.37105],"tcp_start":[0.51768,0.10879,0.38052],"tcp_to_object_dist_end":0.35446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5247,0.03191,0.02602],"object_pos_start":[0.5247,0.03191,0.02602],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.1848,"object_z_max":0.02602,"peak_contact_force":72.23523,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1227.0,"raw_peak_contact_force":313.02814,"subtask_id":"release_1","tcp_end":[0.52367,0.11229,0.38474],"tcp_start":[0.52038,0.11299,0.37105],"tcp_to_object_dist_end":0.36762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":489.0,"n_steps_budget":930.0,"object_pos_end":[0.5247,0.03191,0.02602],"object_pos_start":[0.5247,0.03191,0.02602],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.1848,"object_z_max":0.02602,"peak_contact_force":203.29801,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2445.0,"raw_peak_contact_force":276.70047,"tcp_end":[0.52472,0.11042,0.51493],"tcp_start":[0.52367,0.11229,0.38474],"tcp_to_object_dist_end":0.49517,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```