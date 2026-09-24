## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0062 | 0.44 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | admittance_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0179 | 0.41 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.1415 | 0.34 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | 0.0156 | 0.50 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0375 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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

## Current Skill (Q=-0.006) — your mutation base

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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
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
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: grasp_1
- id: lift_1
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
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
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: close
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=reduce_speed
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.006
- **task_score** (E): 0.435
- **fitness_score**: 0.694  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1605 |
| descend_1 | 1.00 | 1.00 | 0.1057 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.67 | 1.00 | 0.0953 |
| transport_1 | 0.67 | 1.00 | 0.2178 |
| place_1 | 0.67 | 1.00 | 0.0328 |
| release_1 | 1.00 | 0.67 | 0.0153 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.013, 0.146) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 6.528 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.491, -0.013, 0.146)→(0.488, -0.015, 0.040) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.040)→(0.481, -0.015, 0.032) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.333 | 0.133 | 0.172 |
| lift_1 | lift | 0.67 / step_budget | (0.481, -0.015, 0.032)→(0.486, -0.015, 0.127) | (0.493, -0.015, 0.026)→(0.494, -0.015, 0.113) | 0.281→0.248 | 1.00 / 40.667 | 0.073 | 0.552 |
| transport_1 | approach | 0.67 / step_budget | (0.486, -0.015, 0.127)→(0.609, 0.144, 0.207) | (0.494, -0.015, 0.113)→(0.598, 0.137, 0.069) | 0.248→0.149 | 1.00 / 15.333 | 0.124 | 1.375 |
| place_1 | descend | 0.67 / step_budget | (0.609, 0.144, 0.207)→(0.618, 0.157, 0.179) | (0.598, 0.137, 0.069)→(0.600, 0.140, 0.056) | 0.149→0.139 | 1.00 / 12.000 | 3249.634 | 0.179 |
| release_1 | grasp | 1.00 / step_budget | (0.618, 0.157, 0.179)→(0.611, 0.155, 0.166) | (0.600, 0.140, 0.056)→(0.598, 0.144, 0.039) | 0.139→0.140 | 0.67 / 5.667 | 0.082 | 0.204 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.722
- phase_score: 0.346
- phase_breakdown.transport_arc_score: 0.133
- phase_breakdown.approach_1_score: 0.044
- phase_breakdown.descend_1_score: 0.792
- phase_breakdown.release_1_score: 0.272
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.840

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.840
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.722
- **Median Q (composite search score)**: -0.074
- **K-run variance**: 0.0107
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.316


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08714,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12135,"approach_1.speed":0.06361,"descend_1.grasp_z_offset":0.01911,"descend_1.speed":0.02403,"lift_1.lift_height":0.13359,"lift_1.speed":0.04111,"place_1.place_z_offset":-0.03252,"place_1.speed":0.03358,"release_1.duration":0.26118,"transport_1.arc_height":0.08149,"transport_1.speed":0.3211},"optimized_scores":{"best_composite_score":-0.07392,"best_fitness_score":0.62608,"best_task_score":0.30929},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":381.0,"contact_point_centroid":[0.61059,0.14278,-0.00517],"force_p95":0.99738,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55845,"mean_force":0.2471,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60043,0.12751,0.2172]},{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.47236,-0.01957,-0.00117],"force_p95":0.37,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4463,"mean_force":0.0848,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46301,-0.01969,0.0412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9499.0,"contact_point_centroid":[0.50187,-0.00335,0.18793],"force_p95":0.16264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39476,"mean_force":0.0818,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4987,0.01547,0.18722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19898.0,"contact_point_centroid":[0.465,-0.00047,0.08705],"force_p95":0.07371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25392,"mean_force":0.05058,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46517,-0.01965,0.08494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20846.0,"contact_point_centroid":[0.46496,-0.03877,0.08709],"force_p95":0.07063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25386,"mean_force":0.04875,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46519,-0.01965,0.08524]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11454.0,"contact_point_centroid":[0.51197,0.04405,0.19825],"force_p95":0.10225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25226,"mean_force":0.06761,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50795,0.0257,0.19694]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02008,-0.00204],"force_p95":0.13417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17135,"mean_force":0.12582,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46536,-0.01976,0.0408]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4868,-0.00876,0.23071]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.61054,0.14268,-0.00199],"force_p95":0.12283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12673,"mean_force":0.1227,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61189,0.14262,0.18463]},{"body_a":"world","body_b":"grasp_target","contact_count":3028.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47163,-0.01896,0.1012]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.61054,0.14268,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"grasp","tcp_position_centroid":[0.6114,0.14635,0.16074]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5084.0,"contact_point_centroid":[0.46376,-0.00048,0.04245],"force_p95":0.06567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0962,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46427,-0.01973,0.03971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5380.0,"contact_point_centroid":[0.46367,-0.03898,0.0419],"force_p95":0.06461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08362,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46427,-0.01973,0.03971]},{"body_a":"left_finger","body_b":"right_finger","contact_count":193.0,"contact_point_centroid":[0.60487,0.13198,0.21626],"force_p95":0.01487,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01172,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60456,0.13198,0.21369]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1885.0,"contact_point_centroid":[0.61161,0.14637,0.163],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01549,"mean_force":0.01063,"phase_index":6.0,"phase_name":"release_1","phase_type":"grasp","tcp_position_centroid":[0.6114,0.14635,0.16075]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4201.0,"contact_point_centroid":[0.61206,0.14262,0.18696],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.0106,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61189,0.14262,0.18464]}],"total_contact_groups":16},"final_pose_error":0.02356,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61054,0.14268,0.01602],"final_tcp_position":[0.61701,0.14781,0.17226],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.55845,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1764.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4749,-0.01808,0.16079],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47167,-0.01991,0.04721],"tcp_start":[0.4749,-0.01808,0.16079],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.0198,0.02585],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28831,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13278,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.17135,"subtask_id":"grasp_1","tcp_end":[0.46424,-0.01973,0.03968],"tcp_start":[0.47167,-0.01991,0.04721],"tcp_to_object_dist_end":0.0182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47537,-0.01954,0.11004],"object_pos_start":[0.47607,-0.0198,0.02585],"object_to_goal_dist_end":0.25039,"object_to_goal_dist_start":0.28831,"object_z_max":0.10997,"peak_contact_force":0.06963,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40915.0,"raw_peak_contact_force":0.4463,"tcp_end":[0.46972,-0.01967,0.1302],"tcp_start":[0.46424,-0.01973,0.03968],"tcp_to_object_dist_end":0.02094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61056,0.14279,0.01644],"object_pos_start":[0.47537,-0.01954,0.11004],"object_to_goal_dist_end":0.17559,"object_to_goal_dist_start":0.25039,"object_z_max":0.20668,"peak_contact_force":0.1263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21527.0,"raw_peak_contact_force":1.55845,"subtask_id":"transport_arc","tcp_end":[0.60746,0.13563,0.21032],"tcp_start":[0.46972,-0.01967,0.1302],"tcp_to_object_dist_end":0.19403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61054,0.14268,0.01602],"object_pos_start":[0.61056,0.14279,0.01644],"object_to_goal_dist_end":0.17602,"object_to_goal_dist_start":0.17559,"object_z_max":0.01644,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8201.0,"raw_peak_contact_force":0.12673,"tcp_end":[0.61701,0.14781,0.17226],"tcp_start":[0.60746,0.13563,0.21032],"tcp_to_object_dist_end":0.15646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61054,0.14268,0.01602],"object_pos_start":[0.61054,0.14268,0.01602],"object_to_goal_dist_end":0.17602,"object_to_goal_dist_start":0.17602,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3685.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61037,0.14608,0.15866],"tcp_start":[0.61701,0.14781,0.17226],"tcp_to_object_dist_end":0.14268,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06182,"average_solve_count":275.0,"average_success_count":275.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14692,"approach_1.speed":0.03488,"descend_1.grasp_z_offset":0.0106,"descend_1.speed":0.03706,"lift_1.lift_height":0.18387,"lift_1.speed":0.03203,"place_1.place_z_offset":-0.01282,"place_1.speed":0.01999,"release_1.duration":0.39315,"transport_1.arc_height":0.12702,"transport_1.speed":0.2765},"optimized_scores":{"best_composite_score":0.14008,"best_fitness_score":0.84008,"best_task_score":0.72184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.4544,-0.02516,-0.00121],"force_p95":0.42729,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51895,"mean_force":0.10616,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4458,-0.02568,0.03371]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13997.0,"contact_point_centroid":[0.50945,0.0318,0.20415],"force_p95":0.11247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43519,"mean_force":0.07258,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50609,0.05063,0.20343]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3140.0,"contact_point_centroid":[0.60007,0.15686,0.15576],"force_p95":0.15015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36709,"mean_force":0.11322,"phase_index":6.0,"phase_name":"release_1","phase_type":"grasp","tcp_position_centroid":[0.59562,0.1751,0.15937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14522.0,"contact_point_centroid":[0.51413,0.07539,0.20546],"force_p95":0.10801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34677,"mean_force":0.06785,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51077,0.0567,0.20425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13252.0,"contact_point_centroid":[0.60141,0.15484,0.17791],"force_p95":0.12373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28845,"mean_force":0.07171,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59855,0.17367,0.17892]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21114.0,"contact_point_centroid":[0.44643,-0.0447,0.08495],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2407,"mean_force":0.04808,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44669,-0.0256,0.08288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15054.0,"contact_point_centroid":[0.59958,0.19225,0.17752],"force_p95":0.10175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2403,"mean_force":0.06355,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59852,0.17363,0.17907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19309.0,"contact_point_centroid":[0.44656,-0.00641,0.084],"force_p95":0.07468,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23161,"mean_force":0.05176,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44662,-0.0256,0.08154]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02622,-0.00205],"force_p95":0.13813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1882,"mean_force":0.12681,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44816,-0.02578,0.03325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3948.0,"contact_point_centroid":[0.59842,0.19311,0.15506],"force_p95":0.13475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15922,"mean_force":0.09262,"phase_index":6.0,"phase_name":"release_1","phase_type":"grasp","tcp_position_centroid":[0.59567,0.17512,0.15947]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47977,-0.01112,0.2436]},{"body_a":"world","body_b":"grasp_target","contact_count":3696.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45552,-0.02456,0.10942]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.44639,-0.00648,0.0338],"force_p95":0.06502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09849,"mean_force":0.04111,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4471,-0.02573,0.03224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5399.0,"contact_point_centroid":[0.4464,-0.04501,0.03359],"force_p95":0.06511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08608,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4471,-0.02574,0.03224]}],"total_contact_groups":14},"final_pose_error":0.08117,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59727,0.18751,0.08442],"final_tcp_position":[0.60098,0.1768,0.17024],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":19.33743,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":19.33743,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45997,-0.02319,0.18613],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45429,-0.02601,0.03914],"tcp_start":[0.45997,-0.02319,0.18613],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02582,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30339,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1363,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12508.0,"raw_peak_contact_force":0.1882,"subtask_id":"grasp_1","tcp_end":[0.44707,-0.02573,0.03221],"tcp_start":[0.45429,-0.02601,0.03914],"tcp_to_object_dist_end":0.01306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45686,-0.0255,0.11777],"object_pos_start":[0.45845,-0.02582,0.02581],"object_to_goal_dist_end":0.29096,"object_to_goal_dist_start":0.30339,"object_z_max":0.11769,"peak_contact_force":0.07549,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40588.0,"raw_peak_contact_force":0.51895,"tcp_end":[0.44984,-0.02562,0.13084],"tcp_start":[0.44707,-0.02573,0.03221],"tcp_to_object_dist_end":0.01483,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59841,0.1692,0.17452],"object_pos_start":[0.45686,-0.0255,0.11777],"object_to_goal_dist_end":0.07859,"object_to_goal_dist_start":0.29096,"object_z_max":0.2201,"peak_contact_force":0.12183,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28519.0,"raw_peak_contact_force":0.43519,"subtask_id":"transport_arc","tcp_end":[0.59754,0.16923,0.20108],"tcp_start":[0.44984,-0.02562,0.13084],"tcp_to_object_dist_end":0.02657,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60427,0.177,0.13734],"object_pos_start":[0.59841,0.1692,0.17452],"object_to_goal_dist_end":0.04671,"object_to_goal_dist_start":0.07859,"object_z_max":0.17452,"peak_contact_force":0.1347,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28306.0,"raw_peak_contact_force":0.28845,"tcp_end":[0.60098,0.1768,0.17024],"tcp_start":[0.59754,0.16923,0.20108],"tcp_to_object_dist_end":0.03307,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59727,0.18751,0.08442],"object_pos_start":[0.60427,0.177,0.13734],"object_to_goal_dist_end":0.04889,"object_to_goal_dist_start":0.04671,"object_z_max":0.13734,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7088.0,"raw_peak_contact_force":0.36709,"subtask_id":"release_1","tcp_end":[0.59442,0.17472,0.15696],"tcp_start":[0.60098,0.1768,0.17024],"tcp_to_object_dist_end":0.07372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09955,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05284,"approach_1.speed":0.02185,"descend_1.grasp_z_offset":0.01149,"descend_1.speed":0.04971,"lift_1.lift_height":0.11883,"lift_1.speed":0.06049,"place_1.place_z_offset":0.01082,"place_1.speed":0.02714,"release_1.duration":0.35547,"transport_1.arc_height":0.06907,"transport_1.speed":0.20839},"optimized_scores":{"best_composite_score":-0.08486,"best_fitness_score":0.61514,"best_task_score":0.27387},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1157.0,"contact_point_centroid":[0.58666,0.10023,-0.00297],"force_p95":0.50351,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13098,"mean_force":0.16557,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60642,0.10307,0.21602]},{"body_a":"world","body_b":"grasp_target","contact_count":210.0,"contact_point_centroid":[0.54076,0.00072,-0.00114],"force_p95":0.4593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69176,"mean_force":0.09056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52908,0.00085,0.02525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19493.0,"contact_point_centroid":[0.5328,-0.01836,0.07478],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30899,"mean_force":0.05239,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53229,0.00075,0.07297]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19497.0,"contact_point_centroid":[0.53274,0.01986,0.07366],"force_p95":0.07711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2951,"mean_force":0.05252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5322,0.00075,0.07193]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8277.0,"contact_point_centroid":[0.54819,-0.00165,0.16184],"force_p95":0.14328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28211,"mean_force":0.07316,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.546,0.01716,0.16232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8862.0,"contact_point_centroid":[0.54973,0.03742,0.1647],"force_p95":0.13596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27541,"mean_force":0.07112,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54711,0.01876,0.165]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00202],"force_p95":0.13098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15708,"mean_force":0.12512,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53194,0.00091,0.0251]},{"body_a":"world","body_b":"grasp_target","contact_count":3032.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51733,0.0005,0.19353]},{"body_a":"world","body_b":"grasp_target","contact_count":3756.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5368,0.001,0.05312]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58641,0.10031,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62791,0.13684,0.19802]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.58641,0.10031,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"grasp","tcp_position_centroid":[0.62948,0.14419,0.18343]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4117.0,"contact_point_centroid":[0.5313,-0.01831,0.02642],"force_p95":0.07598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10856,"mean_force":0.05169,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53069,0.00089,0.02366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53133,0.01997,0.02554],"force_p95":0.06791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0959,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53069,0.00089,0.02366]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1040.0,"contact_point_centroid":[0.60945,0.10705,0.21789],"force_p95":0.01198,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.01066,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60921,0.10704,0.21556]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4200.0,"contact_point_centroid":[0.62799,0.13683,0.2003],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.0106,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.6279,0.13682,0.19803]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1880.0,"contact_point_centroid":[0.62956,0.1442,0.18564],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01065,"phase_index":6.0,"phase_name":"release_1","phase_type":"grasp","tcp_position_centroid":[0.62947,0.14418,0.18341]}],"total_contact_groups":16},"final_pose_error":0.01909,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58641,0.10031,0.01602],"final_tcp_position":[0.63474,0.14553,0.19555],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.64504,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3032.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53729,0.001,0.08968],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3756.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53898,0.00104,0.03326],"tcp_start":[0.53729,0.001,0.08968],"tcp_to_object_dist_end":0.00898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00075,0.02589],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12924,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10792.0,"raw_peak_contact_force":0.15708,"subtask_id":"grasp_1","tcp_end":[0.53066,0.00089,0.02363],"tcp_start":[0.53898,0.00104,0.03326],"tcp_to_object_dist_end":0.01368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54904,0.0007,0.11168],"object_pos_start":[0.54415,0.00075,0.02589],"object_to_goal_dist_end":0.20198,"object_to_goal_dist_start":0.25051,"object_z_max":0.11157,"peak_contact_force":0.07362,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39200.0,"raw_peak_contact_force":0.69176,"tcp_end":[0.53769,0.0007,0.11988],"tcp_start":[0.53066,0.00089,0.02363],"tcp_to_object_dist_end":0.01401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58641,0.10031,0.01602],"object_pos_start":[0.54904,0.0007,0.11168],"object_to_goal_dist_end":0.19427,"object_to_goal_dist_start":0.20198,"object_z_max":0.1906,"peak_contact_force":0.12262,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19336.0,"raw_peak_contact_force":2.13098,"subtask_id":"transport_arc","tcp_end":[0.62298,0.12712,0.20857],"tcp_start":[0.53769,0.0007,0.11988],"tcp_to_object_dist_end":0.19781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58641,0.10031,0.01602],"object_pos_start":[0.58641,0.10031,0.01602],"object_to_goal_dist_end":0.19427,"object_to_goal_dist_start":0.19427,"object_z_max":0.01602,"peak_contact_force":9748.64504,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8200.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63474,0.14553,0.19555],"tcp_start":[0.62298,0.12712,0.20857],"tcp_to_object_dist_end":0.19134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58641,0.10031,0.01602],"object_pos_start":[0.58641,0.10031,0.01602],"object_to_goal_dist_end":0.19427,"object_to_goal_dist_start":0.19427,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3680.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62851,0.14393,0.18122],"tcp_start":[0.63474,0.14553,0.19555],"tcp_to_object_dist_end":0.17598,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```