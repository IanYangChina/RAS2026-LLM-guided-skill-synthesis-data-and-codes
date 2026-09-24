## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3365 | 0.57 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1875 | 0.33 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1181 | 0.32 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2618 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0590 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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

## Current Skill (Q=0.337) — your mutation base

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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
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
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
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
    orientation:
      mode: keep_current
  subtask_id: grasp_1
- id: lift_vertical
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
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: reduce_speed
- id: transport
  type: approach
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_approach
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
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_vertical** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=reduce_speed
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_approach** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.337
- **task_score** (E): 0.573
- **fitness_score**: 0.757  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0852 |
| descend_1 | 1.00 | 1.00 | 0.1756 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_vertical | 1.00 | 1.00 | 0.1615 |
| transport | 1.00 | 1.00 | 0.2143 |
| place_approach | 1.00 | 1.00 | 0.0803 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, -0.001, 0.224) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.494, -0.001, 0.224)→(0.492, 0.001, 0.049) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.049)→(0.484, 0.000, 0.040) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.333 | 0.142 | 0.194 |
| lift_vertical | lift | 1.00 / step_budget | (0.484, 0.000, 0.040)→(0.481, 0.000, 0.201) | (0.497, 0.001, 0.026)→(0.495, 0.000, 0.180) | 0.266→0.213 | 1.00 / 27.667 | 91001.849 | 0.529 |
| transport | approach | 1.00 / step_budget | (0.481, 0.000, 0.201)→(0.575, 0.173, 0.274) | (0.495, 0.000, 0.180)→(0.576, 0.166, 0.106) | 0.213→0.128 | 1.00 / 15.333 | 3249.723 | 1.342 |
| place_approach | descend | 1.00 / step_budget | (0.575, 0.173, 0.274)→(0.579, 0.182, 0.194) | (0.576, 0.166, 0.106)→(0.574, 0.169, 0.080) | 0.128→0.110 | 1.00 / 20.333 | 0.105 | 0.143 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.104
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.330
- phase_breakdown.approach_1_score: 0.028
- phase_breakdown.descend_1_score: 0.889
- phase_breakdown.transport_arc_score: 0.163
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- grasp_place_fitness: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.262
- **K-run variance**: 0.0240
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.267


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41048,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1711,"descend_1.grasp_z_offset":0.01213,"lift_vertical.lift_height":0.25639,"lift_vertical.lift_speed":0.05658,"place_approach.place_speed":0.49246,"transport.transport_speed":0.06548},"optimized_scores":{"best_composite_score":0.55221,"best_fitness_score":0.97221,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.51072,-0.02212,-0.0014],"force_p95":0.42569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50221,"mean_force":0.13275,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49943,-0.02242,0.03898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15174.0,"contact_point_centroid":[0.49787,-0.00325,0.15792],"force_p95":0.07985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30949,"mean_force":0.05625,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49717,-0.02235,0.15553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15658.0,"contact_point_centroid":[0.49786,-0.04141,0.15491],"force_p95":0.07934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29224,"mean_force":0.05497,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49716,-0.02235,0.15274]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4552.0,"contact_point_centroid":[0.54912,0.16124,0.27113],"force_p95":0.07904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1817,"mean_force":0.05274,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.54815,0.14224,0.2695]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02288,-0.00205],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17251,"mean_force":0.12691,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50177,-0.02247,0.03907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4838.0,"contact_point_centroid":[0.549,0.12322,0.27034],"force_p95":0.08341,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16925,"mean_force":0.05135,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.54819,0.14238,0.26838]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.5137,-0.02302,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50331,-0.00947,0.25488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.5011,-0.00324,0.04056],"force_p95":0.07748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12774,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5006,-0.02245,0.03779]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50741,-0.02115,0.12715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8229.0,"contact_point_centroid":[0.52327,0.07615,0.29265],"force_p95":0.08758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09342,"mean_force":0.0594,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5217,0.05708,0.29073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9368.0,"contact_point_centroid":[0.52275,0.03667,0.29152],"force_p95":0.07914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09258,"mean_force":0.05293,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52121,0.05556,0.29034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.50116,-0.04153,0.03962],"force_p95":0.06961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08985,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5006,-0.02245,0.03779]}],"total_contact_groups":12},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54506,0.14764,0.20704],"final_tcp_position":[0.55008,0.1482,0.23032],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.50221,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1172.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5086,-0.01976,0.20906],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50877,-0.02264,0.04684],"tcp_start":[0.5086,-0.01976,0.20906],"tcp_to_object_dist_end":0.0214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.0224,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26538,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13533,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10810.0,"raw_peak_contact_force":0.17251,"subtask_id":"grasp_1","tcp_end":[0.50057,-0.02244,0.03775],"tcp_start":[0.50877,-0.02264,0.04684],"tcp_to_object_dist_end":0.01768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,-0.02241,0.25577],"object_pos_start":[0.5136,-0.0224,0.02581],"object_to_goal_dist_end":0.1837,"object_to_goal_dist_start":0.26538,"object_z_max":0.25551,"peak_contact_force":0.07951,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30916.0,"raw_peak_contact_force":0.50221,"tcp_end":[0.49798,-0.02237,0.27454],"tcp_start":[0.50057,-0.02244,0.03775],"tcp_to_object_dist_end":0.02044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.55322,0.13646,0.28906],"object_pos_start":[0.50607,-0.02241,0.25577],"object_to_goal_dist_end":0.06877,"object_to_goal_dist_start":0.1837,"object_z_max":0.28899,"peak_contact_force":0.08411,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17597.0,"raw_peak_contact_force":0.09342,"subtask_id":"transport_arc","tcp_end":[0.5474,0.1365,0.31107],"tcp_start":[0.49798,-0.02237,0.27454],"tcp_to_object_dist_end":0.02277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.54506,0.14764,0.20704],"object_pos_start":[0.55322,0.13646,0.28906],"object_to_goal_dist_end":0.01792,"object_to_goal_dist_start":0.06877,"object_z_max":0.28906,"peak_contact_force":0.0696,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9390.0,"raw_peak_contact_force":0.1817,"tcp_end":[0.55008,0.1482,0.23032],"tcp_start":[0.5474,0.1365,0.31107],"tcp_to_object_dist_end":0.02382,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03077,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24761,"descend_1.grasp_z_offset":0.01091,"lift_vertical.lift_height":0.15727,"lift_vertical.lift_speed":0.24477,"place_approach.place_speed":0.32229,"transport.transport_speed":0.32658},"optimized_scores":{"best_composite_score":0.26167,"best_fitness_score":0.68167,"best_task_score":0.41722},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.57124,0.23745,-0.00814],"force_p95":1.07382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00333,"mean_force":0.40823,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55396,0.22353,0.23227]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.49863,0.04274,-0.00144],"force_p95":0.58033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61709,"mean_force":0.11093,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48722,0.04323,0.0386]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6094.0,"contact_point_centroid":[0.48766,0.06199,0.09642],"force_p95":0.11122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34824,"mean_force":0.06853,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48519,0.04304,0.09443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5826.0,"contact_point_centroid":[0.48787,0.02414,0.0997],"force_p95":0.10945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34618,"mean_force":0.07065,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48519,0.04304,0.09747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3497.0,"contact_point_centroid":[0.5137,0.08804,0.19383],"force_p95":0.17151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26816,"mean_force":0.10722,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50823,0.10666,0.19288]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04485,-0.00215],"force_p95":0.16288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23175,"mean_force":0.13349,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4897,0.04347,0.03831]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4738.0,"contact_point_centroid":[0.51785,0.134,0.19683],"force_p95":0.11856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19502,"mean_force":0.07941,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51174,0.11597,0.19584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.48843,0.02412,0.04017],"force_p95":0.07053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15553,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48856,0.04337,0.03709]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.50118,0.04505,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49839,0.0173,0.28761]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.57096,0.23759,-0.00202],"force_p95":0.1245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12515,"mean_force":0.11684,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55734,0.2355,0.19482]},{"body_a":"world","body_b":"grasp_target","contact_count":2844.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49633,0.03977,0.15996]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5519.0,"contact_point_centroid":[0.48825,0.06269,0.03958],"force_p95":0.07022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07454,"mean_force":0.04097,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48856,0.04337,0.03709]},{"body_a":"left_finger","body_b":"right_finger","contact_count":958.0,"contact_point_centroid":[0.55785,0.2356,0.19633],"force_p95":0.01257,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01074,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55734,0.23557,0.19416]}],"total_contact_groups":13},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57096,0.23759,0.01602],"final_tcp_position":[0.55947,0.24083,0.15427],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273005.36003,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49821,0.03561,0.27674],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2844.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49659,0.04409,0.04575],"tcp_start":[0.49821,0.03561,0.27674],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50112,0.04374,0.02549],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24324,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15693,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12352.0,"raw_peak_contact_force":0.23175,"subtask_id":"grasp_1","tcp_end":[0.48853,0.04336,0.03706],"tcp_start":[0.49659,0.04409,0.04575],"tcp_to_object_dist_end":0.0171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":389.0,"n_steps_budget":600.0,"object_pos_end":[0.50297,0.04348,0.15548],"object_pos_start":[0.50112,0.04374,0.02549],"object_to_goal_dist_end":0.21073,"object_to_goal_dist_start":0.24324,"object_z_max":0.15521,"peak_contact_force":273005.36003,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11994.0,"raw_peak_contact_force":0.61709,"tcp_end":[0.48535,0.04305,0.17463],"tcp_start":[0.48853,0.04336,0.03706],"tcp_to_object_dist_end":0.02603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.57106,0.23722,0.01149],"object_pos_start":[0.50297,0.04348,0.15548],"object_to_goal_dist_end":0.13566,"object_to_goal_dist_start":0.21073,"object_z_max":0.18764,"peak_contact_force":0.06285,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8417.0,"raw_peak_contact_force":2.00333,"subtask_id":"transport_arc","tcp_end":[0.55682,0.23108,0.23479],"tcp_start":[0.48535,0.04305,0.17463],"tcp_to_object_dist_end":0.22384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.57096,0.23759,0.01602],"object_pos_start":[0.57106,0.23722,0.01149],"object_to_goal_dist_end":0.13112,"object_to_goal_dist_start":0.13566,"object_z_max":0.01667,"peak_contact_force":0.12263,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1878.0,"raw_peak_contact_force":0.12515,"tcp_end":[0.55947,0.24083,0.15427],"tcp_start":[0.55682,0.23108,0.23479],"tcp_to_object_dist_end":0.13877,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10317,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14714,"descend_1.grasp_z_offset":0.0182,"lift_vertical.lift_height":0.12948,"lift_vertical.lift_speed":0.38382,"place_approach.place_speed":0.23703,"transport.transport_speed":0.20207},"optimized_scores":{"best_composite_score":0.19567,"best_fitness_score":0.61567,"best_task_score":0.30189},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":705.0,"contact_point_centroid":[0.60487,0.12294,-0.00366],"force_p95":0.7363,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92858,"mean_force":0.19132,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60276,0.13096,0.26141]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.47394,-0.01922,-0.00137],"force_p95":0.40318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46653,"mean_force":0.10246,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46306,-0.0196,0.04658]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5073.0,"contact_point_centroid":[0.46318,-0.0005,0.09434],"force_p95":0.11107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33952,"mean_force":0.06849,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46101,-0.01954,0.09258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5654.0,"contact_point_centroid":[0.46311,-0.0385,0.0936],"force_p95":0.10521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30548,"mean_force":0.06259,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46102,-0.01954,0.09194]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.51279,0.01274,0.18779],"force_p95":0.14588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2324,"mean_force":0.08962,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50708,0.03125,0.18895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5137.0,"contact_point_centroid":[0.5148,0.05195,0.18914],"force_p95":0.12858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18391,"mean_force":0.08667,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50923,0.0335,0.19058]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02003,-0.00205],"force_p95":0.13617,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17897,"mean_force":0.12644,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46533,-0.01966,0.04643]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48748,-0.00848,0.24399]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.60511,0.12301,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.6229,0.15304,0.23722]},{"body_a":"world","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47258,-0.0187,0.11934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4477.0,"contact_point_centroid":[0.46426,-0.00037,0.0486],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0967,"mean_force":0.04834,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46424,-0.01963,0.04533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5391.0,"contact_point_centroid":[0.46415,-0.03878,0.04757],"force_p95":0.06358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07766,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46424,-0.01963,0.04533]},{"body_a":"left_finger","body_b":"right_finger","contact_count":558.0,"contact_point_centroid":[0.60828,0.13625,0.26747],"force_p95":0.01374,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01525,"mean_force":0.01081,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60787,0.13624,0.26526]},{"body_a":"left_finger","body_b":"right_finger","contact_count":884.0,"contact_point_centroid":[0.62336,0.15308,0.23913],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01053,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.62292,0.15307,0.23688]}],"total_contact_groups":14},"final_pose_error":0.00973,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60511,0.12301,0.01602],"final_tcp_position":[0.62613,0.15649,0.19773],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9749.02207,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4757,-0.01769,0.18655],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4719,-0.01981,0.05314],"tcp_start":[0.4757,-0.01769,0.18655],"tcp_to_object_dist_end":0.02746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01965,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13395,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11668.0,"raw_peak_contact_force":0.17897,"subtask_id":"grasp_1","tcp_end":[0.46421,-0.01963,0.0453],"tcp_start":[0.4719,-0.01981,0.05314],"tcp_to_object_dist_end":0.02281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":321.0,"n_steps_budget":600.0,"object_pos_end":[0.47694,-0.01966,0.12989],"object_pos_start":[0.47609,-0.01965,0.02582],"object_to_goal_dist_end":0.24386,"object_to_goal_dist_start":0.28822,"object_z_max":0.12962,"peak_contact_force":0.10631,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10795.0,"raw_peak_contact_force":0.46653,"tcp_end":[0.46092,-0.01952,0.15528],"tcp_start":[0.46421,-0.01963,0.0453],"tcp_to_object_dist_end":0.03002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.60511,0.12301,0.01602],"object_pos_start":[0.47694,-0.01966,0.12989],"object_to_goal_dist_end":0.17966,"object_to_goal_dist_start":0.24386,"object_z_max":0.19329,"peak_contact_force":9749.02207,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11372.0,"raw_peak_contact_force":1.92858,"subtask_id":"transport_arc","tcp_end":[0.62127,0.15022,0.27534],"tcp_start":[0.46092,-0.01952,0.15528],"tcp_to_object_dist_end":0.26125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.60511,0.12301,0.01602],"object_pos_start":[0.60511,0.12301,0.01602],"object_to_goal_dist_end":0.17966,"object_to_goal_dist_start":0.17966,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1720.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.62613,0.15649,0.19773],"tcp_start":[0.62127,0.15022,0.27534],"tcp_to_object_dist_end":0.18596,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```